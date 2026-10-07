#include <arpa/inet.h>
#include <arm_neon.h>
#include <errno.h>
#include <iio.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PI 3.14159265358979323846f

#define DEST_IP "192.168.2.10"
#define PORT 5000
#define MAGIC 0x49515048

#define FS_HZ 20000000LL
#define BB_SPACING_HZ 2000000LL

#define FMIN_HZ 1700000000LL
#define FMAX_HZ 2000000000LL

#define NUM_BB_FREQS 10
#define MINI_BUF 400
#define CAPTURE_AVERAGES 50
#define PROCESS_SAMPLES (MINI_BUF * CAPTURE_AVERAGES)
#define RX_BUFFER_SAMPLES (PROCESS_SAMPLES + MINI_BUF)
#define TX_BUFFER_SAMPLES PROCESS_SAMPLES

#define RF_BW_HZ FS_HZ
#define RETUNE_DELAY_US 100

#define LOOPBACK_GAIN_DB 0.0
#define RX_GAIN_DB 54.0
#define TX1_GAIN_DB 0.0
#define TX2_GAIN_DB -37.5

#define TX_SCALE 16384.0f

#define FASTLOCK_SLOTS 8
#define PROFILE_LEN 128

#define PHASORS_PER_PACKET 182

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq;
    uint32_t sweep;
    uint16_t start_bin;
    uint16_t count;
} packet_header_t;

static void print_iio_error(const char *message) {
    char err[256];
    iio_strerror(errno, err, sizeof(err));
    printf("[-] %s: %s (%d)\n", message, err, errno);
}

static inline float hsum(float32x4_t v) {
    float32x2_t x = vadd_f32(
        vget_low_f32(v),
        vget_high_f32(v)
    );

    x = vpadd_f32(x, x);

    return vget_lane_f32(x, 0);
}

/*
 * Baseband tones:
 *
 * -10, -8, -6, -4, -2,
 *   0,  2,  4,  6,  8 MHz
 */
static inline long long bb_frequency(int k) {
    return -FS_HZ / 2 + (long long)k * BB_SPACING_HZ;
}

static inline float schroeder_phase(int k) {
    return -PI * k * (k - 1) / NUM_BB_FREQS;
}

/*
 * Builds:
 *
 * mixers[10][400]
 *
 * Each complex value is stored:
 *
 * real, imag, real, imag...
 */
static void build_mixers(float *mixers) {
    for (int k = 0; k < NUM_BB_FREQS; k++) {
        float f = (float)bb_frequency(k);
        float phase = schroeder_phase(k);

        for (int n = 0; n < MINI_BUF; n++) {
            float angle =
                -2.0f * PI * f * n / (float)FS_HZ
                - phase;

            int p = 2 * (k * MINI_BUF + n);

            mixers[p] = cosf(angle);
            mixers[p + 1] = sinf(angle);
        }
    }
}

/*
 * Generate the cyclic 10-tone TX waveform.
 */
static void fill_tx_buffer(
    struct iio_buffer *buf,
    struct iio_channel *tx1_i,
    struct iio_channel *tx1_q,
    struct iio_channel *tx2_i,
    struct iio_channel *tx2_q
) {
    ptrdiff_t step = iio_buffer_step(buf);

    char *p1i = iio_buffer_first(buf, tx1_i);
    char *p1q = iio_buffer_first(buf, tx1_q);
    char *p2i = iio_buffer_first(buf, tx2_i);
    char *p2q = iio_buffer_first(buf, tx2_q);

    for (int n = 0; n < TX_BUFFER_SAMPLES; n++) {
        float re = 0.0f;
        float im = 0.0f;

        for (int k = 0; k < NUM_BB_FREQS; k++) {
            float f = (float)bb_frequency(k);
            float phase = schroeder_phase(k);

            float angle =
                2.0f * PI * f * n / (float)FS_HZ
                + phase;

            re += cosf(angle);
            im += sinf(angle);
        }

        re *= TX_SCALE / NUM_BB_FREQS;
        im *= TX_SCALE / NUM_BB_FREQS;

        if (re > 32767.0f) re = 32767.0f;
        if (re < -32768.0f) re = -32768.0f;

        if (im > 32767.0f) im = 32767.0f;
        if (im < -32768.0f) im = -32768.0f;

        int16_t I = (int16_t)lrintf(re);
        int16_t Q = (int16_t)lrintf(im);

        *(int16_t *)p1i = I;
        *(int16_t *)p1q = Q;
        *(int16_t *)p2i = I;
        *(int16_t *)p2q = Q;

        p1i += step;
        p1q += step;
        p2i += step;
        p2q += step;
    }
}

/*
 * Capture one RX buffer.
 *
 * RX_BUFFER_SAMPLES = 20400
 *
 * Layout of output arrays:
 *
 * I0,Q0,I1,Q1,...
 */
static int read_rx(
    struct iio_buffer *buf,
    struct iio_channel *lb_i,
    struct iio_channel *lb_q,
    struct iio_channel *rc_i,
    struct iio_channel *rc_q,
    float *loop_raw,
    float *rx_raw
) {
    ssize_t ret = iio_buffer_refill(buf);

    if (ret < 0) {
        printf("[-] RX refill failed: %zd\n", ret);
        return -1;
    }

    ptrdiff_t step = iio_buffer_step(buf);

    char *pli = iio_buffer_first(buf, lb_i);
    char *plq = iio_buffer_first(buf, lb_q);
    char *pri = iio_buffer_first(buf, rc_i);
    char *prq = iio_buffer_first(buf, rc_q);

    if (!pli || !plq || !pri || !prq) {
        printf("[-] Failed locating RX channels in buffer\n");
        return -1;
    }

    const struct iio_data_format *fmt =
        iio_channel_get_data_format(lb_i);

    int shift = fmt ? fmt->shift : 0;

    for (int n = 0; n < RX_BUFFER_SAMPLES; n++) {
        int16_t li = *(int16_t *)pli;
        int16_t lq = *(int16_t *)plq;
        int16_t ri = *(int16_t *)pri;
        int16_t rq = *(int16_t *)prq;

        if (shift > 0) {
            li >>= shift;
            lq >>= shift;
            ri >>= shift;
            rq >>= shift;
        }

        loop_raw[2 * n] = (float)li;
        loop_raw[2 * n + 1] = (float)lq;

        rx_raw[2 * n] = (float)ri;
        rx_raw[2 * n + 1] = (float)rq;

        pli += step;
        plq += step;
        pri += step;
        prq += step;
    }

    return 0;
}

/*
 * Same operation as Python extract_bb_phasors().
 *
 * Discard first 400 samples.
 *
 * Process:
 *
 * 50 averages
 * 400 samples each
 * 10 baseband frequencies
 */
static void extract_bb_phasors_neon(
    const float *loop_raw,
    const float *rx_raw,
    const float *mixers,
    float *out
) {
    float numerator_re[NUM_BB_FREQS] = {0};
    float numerator_im[NUM_BB_FREQS] = {0};
    float denominator[NUM_BB_FREQS] = {0};

    loop_raw += 2 * MINI_BUF;
    rx_raw += 2 * MINI_BUF;

    const float scale = 1.0f / MINI_BUF;

    for (int avg = 0; avg < CAPTURE_AVERAGES; avg++) {
        const float *loop =
            loop_raw + 2 * avg * MINI_BUF;

        const float *rx =
            rx_raw + 2 * avg * MINI_BUF;

        for (int k = 0; k < NUM_BB_FREQS; k++) {
            const float *m =
                mixers + 2 * k * MINI_BUF;

            float32x4_t lr_acc = vdupq_n_f32(0.0f);
            float32x4_t li_acc = vdupq_n_f32(0.0f);
            float32x4_t rr_acc = vdupq_n_f32(0.0f);
            float32x4_t ri_acc = vdupq_n_f32(0.0f);

            for (int n = 0; n < MINI_BUF; n += 4) {
                float32x4x2_t mv =
                    vld2q_f32(m + 2 * n);

                float32x4x2_t lv =
                    vld2q_f32(loop + 2 * n);

                float32x4x2_t rv =
                    vld2q_f32(rx + 2 * n);

                lr_acc = vmlaq_f32(
                    lr_acc,
                    mv.val[0],
                    lv.val[0]
                );

                lr_acc = vmlsq_f32(
                    lr_acc,
                    mv.val[1],
                    lv.val[1]
                );

                li_acc = vmlaq_f32(
                    li_acc,
                    mv.val[0],
                    lv.val[1]
                );

                li_acc = vmlaq_f32(
                    li_acc,
                    mv.val[1],
                    lv.val[0]
                );

                rr_acc = vmlaq_f32(
                    rr_acc,
                    mv.val[0],
                    rv.val[0]
                );

                rr_acc = vmlsq_f32(
                    rr_acc,
                    mv.val[1],
                    rv.val[1]
                );

                ri_acc = vmlaq_f32(
                    ri_acc,
                    mv.val[0],
                    rv.val[1]
                );

                ri_acc = vmlaq_f32(
                    ri_acc,
                    mv.val[1],
                    rv.val[0]
                );
            }

            float lr = hsum(lr_acc) * scale;
            float li = hsum(li_acc) * scale;

            float rr = hsum(rr_acc) * scale;
            float ri = hsum(ri_acc) * scale;

            /*
             * rx_phasor * conj(loop_phasor)
             */
            numerator_re[k] +=
                rr * lr + ri * li;

            numerator_im[k] +=
                ri * lr - rr * li;

            denominator[k] +=
                lr * lr + li * li;
        }
    }

    for (int k = 0; k < NUM_BB_FREQS; k++) {
        float d =
            denominator[k] + 1e-12f;

        out[2 * k] =
            numerator_re[k] / d;

        out[2 * k + 1] =
            numerator_im[k] / d;
    }
}

/*
 * Save the currently tuned Fastlock profile.
 */
static int save_fastlock_profile(
    struct iio_channel *lo,
    char *profile
) {
    if (iio_channel_attr_write(
        lo,
        "fastlock_store",
        "0"
    ) < 0)
        return -1;

    ssize_t len =
        iio_channel_attr_read(
            lo,
            "fastlock_save",
            profile,
            PROFILE_LEN - 1
        );

    if (len < 0)
        return -1;

    profile[len] = '\0';

    return 0;
}

/*
 * Load a stored profile into one of the 8 hardware slots.
 */
static int load_fastlock_profile(
    struct iio_channel *lo,
    int slot,
    const char *profile
) {
    const char *space = strchr(profile, ' ');

    if (!space)
        return -1;

    char load[PROFILE_LEN];

    snprintf(
        load,
        sizeof(load),
        "%d%s",
        slot,
        space
    );

    return iio_channel_attr_write(
        lo,
        "fastlock_load",
        load
    );
}

static int recall_fastlock(
    struct iio_channel *rx_lo,
    struct iio_channel *tx_lo,
    int slot
) {
    char slot_string[8];

    snprintf(
        slot_string,
        sizeof(slot_string),
        "%d",
        slot
    );

    if (iio_channel_attr_write(
        rx_lo,
        "fastlock_recall",
        slot_string
    ) < 0)
        return -1;

    if (iio_channel_attr_write(
        tx_lo,
        "fastlock_recall",
        slot_string
    ) < 0)
        return -1;

    return 0;
}

/*
 * Sends one complete frequency-domain range-profile vector.
 *
 * Complex float32:
 *
 * real = 4 bytes
 * imag = 4 bytes
 *
 * 182 complex samples = 1456 bytes
 * header = 16 bytes
 *
 * total UDP payload = 1472 bytes
 */
static int send_sweep(
    int sock,
    struct sockaddr_in *dst,
    const float *sweep_data,
    int num_bins,
    uint32_t sweep_id,
    uint32_t *seq
) {
    uint8_t packet[
        sizeof(packet_header_t)
        + PHASORS_PER_PACKET * 2 * sizeof(float)
    ];

    for (
        int start = 0;
        start < num_bins;
        start += PHASORS_PER_PACKET
    ) {
        int count = num_bins - start;

        if (count > PHASORS_PER_PACKET)
            count = PHASORS_PER_PACKET;

        packet_header_t header = {
            .magic = htonl(MAGIC),
            .seq = htonl((*seq)++),
            .sweep = htonl(sweep_id),
            .start_bin = htons((uint16_t)start),
            .count = htons((uint16_t)count)
        };

        memcpy(
            packet,
            &header,
            sizeof(header)
        );

        memcpy(
            packet + sizeof(header),
            sweep_data + 2 * start,
            count * 2 * sizeof(float)
        );

        ssize_t sent = sendto(
            sock,
            packet,
            sizeof(header)
                + count * 2 * sizeof(float),
            0,
            (struct sockaddr *)dst,
            sizeof(*dst)
        );

        if (sent < 0) {
            perror("sendto");
            return -1;
        }
    }

    return 0;
}

int main(void) {
    /*
     * Full requested RF grid:
     *
     * 70 MHz
     * 72 MHz
     * 74 MHz
     * ...
     * 6000 MHz
     */
    int num_output_bins =
        (int)(
            (FMAX_HZ - FMIN_HZ)
            / BB_SPACING_HZ
        ) + 1;

    /*
     * Ten 2 MHz bins are captured per LO position.
     */
    int num_retunes =
        (num_output_bins + NUM_BB_FREQS - 1)
        / NUM_BB_FREQS;

    int packets_per_sweep =
        (num_output_bins
            + PHASORS_PER_PACKET - 1)
        / PHASORS_PER_PACKET;

    printf(
        "[+] Output bins: %d\n",
        num_output_bins
    );

    printf(
        "[+] LO retunes: %d\n",
        num_retunes
    );

    printf(
        "[+] UDP packets/RP: %d\n",
        packets_per_sweep
    );

    /*
     * Allocate processing memory.
     */
    float *mixers = malloc(
        NUM_BB_FREQS
        * MINI_BUF
        * 2
        * sizeof(float)
    );

    float *loop_raw = malloc(
        RX_BUFFER_SAMPLES
        * 2
        * sizeof(float)
    );

    float *rx_raw = malloc(
        RX_BUFFER_SAMPLES
        * 2
        * sizeof(float)
    );

    float *sweep_data = calloc(
        num_output_bins * 2,
        sizeof(float)
    );

    if (
        !mixers ||
        !loop_raw ||
        !rx_raw ||
        !sweep_data
    ) {
        printf("[-] Memory allocation failed\n");
        return 1;
    }

    build_mixers(mixers);

    /*
     * UDP output.
     */
    int sock =
        socket(AF_INET, SOCK_DGRAM, 0);

    if (sock < 0) {
        perror("socket");
        return 1;
    }

    int sndbuf =
        4 * 1024 * 1024;

    setsockopt(
        sock,
        SOL_SOCKET,
        SO_SNDBUF,
        &sndbuf,
        sizeof(sndbuf)
    );

    struct sockaddr_in dst = {
        .sin_family = AF_INET,
        .sin_port = htons(PORT)
    };

    if (
        inet_pton(
            AF_INET,
            DEST_IP,
            &dst.sin_addr
        ) != 1
    ) {
        printf("[-] Invalid destination IP\n");
        return 1;
    }

    /*
     * Local Zynq IIO context.
     */
    struct iio_context *ctx =
        iio_create_local_context();

    if (!ctx) {
        print_iio_error(
            "Could not create local IIO context"
        );
        return 1;
    }

    struct iio_device *sdr =
        iio_context_find_device(
            ctx,
            "ad9361-phy"
        );

    struct iio_device *tx =
        iio_context_find_device(
            ctx,
            "cf-ad9361-dds-core-lpc"
        );

    struct iio_device *rx =
        iio_context_find_device(
            ctx,
            "cf-ad9361-lpc"
        );

    if (!sdr || !tx || !rx) {
        printf("[-] Required IIO device missing\n");
        return 1;
    }

    /*
     * Local oscillators.
     */
    struct iio_channel *tx_lo =
        iio_device_find_channel(
            sdr,
            "altvoltage1",
            true
        );

    struct iio_channel *rx_lo =
        iio_device_find_channel(
            sdr,
            "altvoltage0",
            true
        );

    /*
     * RX1 = loopback
     */
    struct iio_channel *lb_phy =
        iio_device_find_channel(
            sdr,
            "voltage0",
            false
        );

    struct iio_channel *lb_i =
        iio_device_find_channel(
            rx,
            "voltage0",
            false
        );

    struct iio_channel *lb_q =
        iio_device_find_channel(
            rx,
            "voltage1",
            false
        );

    /*
     * RX2 = radar receive
     */
    struct iio_channel *rc_phy =
        iio_device_find_channel(
            sdr,
            "voltage1",
            false
        );

    struct iio_channel *rc_i =
        iio_device_find_channel(
            rx,
            "voltage2",
            false
        );

    struct iio_channel *rc_q =
        iio_device_find_channel(
            rx,
            "voltage3",
            false
        );

    /*
     * TX1
     */
    struct iio_channel *tx1_phy =
        iio_device_find_channel(
            sdr,
            "voltage0",
            true
        );

    struct iio_channel *tx1_i =
        iio_device_find_channel(
            tx,
            "voltage0",
            true
        );

    struct iio_channel *tx1_q =
        iio_device_find_channel(
            tx,
            "voltage1",
            true
        );

    /*
     * TX2
     */
    struct iio_channel *tx2_phy =
        iio_device_find_channel(
            sdr,
            "voltage1",
            true
        );

    struct iio_channel *tx2_i =
        iio_device_find_channel(
            tx,
            "voltage2",
            true
        );

    struct iio_channel *tx2_q =
        iio_device_find_channel(
            tx,
            "voltage3",
            true
        );

    if (
        !tx_lo ||
        !rx_lo ||
        !lb_phy ||
        !lb_i ||
        !lb_q ||
        !rc_phy ||
        !rc_i ||
        !rc_q ||
        !tx1_phy ||
        !tx1_i ||
        !tx1_q ||
        !tx2_phy ||
        !tx2_i ||
        !tx2_q
    ) {
        printf("[-] One or more IIO channels missing\n");
        return 1;
    }

    /*
     * RX configuration.
     */
    iio_channel_attr_write(
        lb_phy,
        "rf_port_select",
        "A_BALANCED"
    );

    iio_channel_attr_write(
        rc_phy,
        "rf_port_select",
        "B_BALANCED"
    );

    iio_channel_attr_write_longlong(
        lb_phy,
        "rf_bandwidth",
        RF_BW_HZ
    );

    iio_channel_attr_write_longlong(
        rc_phy,
        "rf_bandwidth",
        RF_BW_HZ
    );

    iio_channel_attr_write_longlong(
        lb_phy,
        "sampling_frequency",
        FS_HZ
    );

    iio_channel_attr_write_longlong(
        rc_phy,
        "sampling_frequency",
        FS_HZ
    );

    iio_channel_attr_write(
        lb_phy,
        "gain_control_mode",
        "manual"
    );

    iio_channel_attr_write(
        rc_phy,
        "gain_control_mode",
        "manual"
    );

    iio_channel_attr_write_double(
        lb_phy,
        "hardwaregain",
        LOOPBACK_GAIN_DB
    );

    iio_channel_attr_write_double(
        rc_phy,
        "hardwaregain",
        RX_GAIN_DB
    );

    iio_channel_enable(lb_i);
    iio_channel_enable(lb_q);
    iio_channel_enable(rc_i);
    iio_channel_enable(rc_q);

    /*
     * TX configuration.
     */
    iio_channel_attr_write(
        tx1_phy,
        "rf_port_select",
        "A"
    );

    iio_channel_attr_write(
        tx2_phy,
        "rf_port_select",
        "B"
    );

    iio_channel_attr_write_longlong(
        tx1_phy,
        "rf_bandwidth",
        RF_BW_HZ
    );

    iio_channel_attr_write_longlong(
        tx2_phy,
        "rf_bandwidth",
        RF_BW_HZ
    );

    iio_channel_attr_write_longlong(
        tx1_phy,
        "sampling_frequency",
        FS_HZ
    );

    iio_channel_attr_write_longlong(
        tx2_phy,
        "sampling_frequency",
        FS_HZ
    );

    iio_channel_attr_write_double(
        tx1_phy,
        "hardwaregain",
        TX1_GAIN_DB
    );

    iio_channel_attr_write_double(
        tx2_phy,
        "hardwaregain",
        TX2_GAIN_DB
    );

    iio_channel_enable(tx1_i);
    iio_channel_enable(tx1_q);
    iio_channel_enable(tx2_i);
    iio_channel_enable(tx2_q);

    /*
     * Create cyclic TX DMA buffer.
     *
     * This is the ONLY TX buffer creation in the program.
     */
    errno = 0;

    struct iio_buffer *tx_buf =
        iio_device_create_buffer(
            tx,
            TX_BUFFER_SAMPLES,
            true
        );

    if (!tx_buf) {
        print_iio_error(
            "TX buffer creation failed"
        );
        return 1;
    }

    printf(
        "[+] TX buffer created: %d samples\n",
        TX_BUFFER_SAMPLES
    );

    fill_tx_buffer(
        tx_buf,
        tx1_i,
        tx1_q,
        tx2_i,
        tx2_q
    );

    ssize_t tx_push =
        iio_buffer_push(tx_buf);

    if (tx_push < 0) {
        printf(
            "[-] TX push failed: %zd\n",
            tx_push
        );
        return 1;
    }

    printf("[+] Cyclic TX active\n");

    /*
     * Create RX buffer:
     *
     * 20400 samples total
     *
     * 400 discarded
     * 20000 processed
     */
    errno = 0;

    struct iio_buffer *rx_buf =
        iio_device_create_buffer(
            rx,
            RX_BUFFER_SAMPLES,
            false
        );

    if (!rx_buf) {
        print_iio_error(
            "RX buffer creation failed"
        );
        return 1;
    }

    printf(
        "[+] RX buffer created: %d samples\n",
        RX_BUFFER_SAMPLES
    );

    /*
     * Store every LO Fastlock profile in RAM once.
     *
     * 297 LO positions are required for 70 MHz -> 6 GHz.
     */
    char *rx_profiles =
        calloc(
            num_retunes,
            PROFILE_LEN
        );

    char *tx_profiles =
        calloc(
            num_retunes,
            PROFILE_LEN
        );

    if (!rx_profiles || !tx_profiles) {
        printf(
            "[-] Fastlock profile allocation failed\n"
        );
        return 1;
    }

    printf(
        "[+] Generating %d Fastlock profiles...\n",
        num_retunes
    );

    for (int r = 0; r < num_retunes; r++) {
        /*
         * First center is 80 MHz:
         *
         * center - 10 MHz = 70 MHz
         *
         * Last center is 6 GHz.
         */
        long long center =
            FMIN_HZ
            + FS_HZ / 2
            + (long long)r * FS_HZ;

        if (
            iio_channel_attr_write_longlong(
                rx_lo,
                "frequency",
                center
            ) < 0
        ) {
            printf(
                "\n[-] RX LO tune failed at %.3f MHz\n",
                center / 1e6
            );
            return 1;
        }

        if (
            iio_channel_attr_write_longlong(
                tx_lo,
                "frequency",
                center
            ) < 0
        ) {
            printf(
                "\n[-] TX LO tune failed at %.3f MHz\n",
                center / 1e6
            );
            return 1;
        }

        if (
            save_fastlock_profile(
                rx_lo,
                rx_profiles + r * PROFILE_LEN
            ) < 0
        ) {
            printf(
                "\n[-] RX Fastlock save failed at %d\n",
                r
            );
            return 1;
        }

        if (
            save_fastlock_profile(
                tx_lo,
                tx_profiles + r * PROFILE_LEN
            ) < 0
        ) {
            printf(
                "\n[-] TX Fastlock save failed at %d\n",
                r
            );
            return 1;
        }

        printf(
            "\r[+] Profiles: %d/%d",
            r + 1,
            num_retunes
        );

        fflush(stdout);
    }

    printf("\n[+] Fastlock profiles ready\n");

    uint32_t seq = 0;
    uint32_t sweep_id = 0;

    float phasors[
        NUM_BB_FREQS * 2
    ];

    /*
     * Continuous radar acquisition.
     */
    while (1) {
        /*
         * Everything starts at zero.
         *
         * If an LO recall or RX capture fails,
         * those frequency bins remain 0+0j.
         */
        memset(
            sweep_data,
            0,
            num_output_bins
                * 2
                * sizeof(float)
        );

        /*
         * Fastlock supports 8 loaded profiles at a time.
         */
        for (
            int batch = 0;
            batch < num_retunes;
            batch += FASTLOCK_SLOTS
        ) {
            int batch_size =
                num_retunes - batch;

            if (
                batch_size >
                FASTLOCK_SLOTS
            )
                batch_size =
                    FASTLOCK_SLOTS;

            /*
             * Load RX and TX profiles into slots 0-7.
             */
            for (
                int slot = 0;
                slot < batch_size;
                slot++
            ) {
                int r =
                    batch + slot;

                if (
                    load_fastlock_profile(
                        rx_lo,
                        slot,
                        rx_profiles
                            + r * PROFILE_LEN
                    ) < 0
                ) {
                    printf(
                        "[-] RX profile load failed: %d\n",
                        r
                    );
                }

                if (
                    load_fastlock_profile(
                        tx_lo,
                        slot,
                        tx_profiles
                            + r * PROFILE_LEN
                    ) < 0
                ) {
                    printf(
                        "[-] TX profile load failed: %d\n",
                        r
                    );
                }
            }

            /*
             * Recall each slot and capture one RX buffer.
             */
            for (
                int slot = 0;
                slot < batch_size;
                slot++
            ) {
                int r =
                    batch + slot;

                long long center =
                    FMIN_HZ
                    + FS_HZ / 2
                    + (long long)r
                        * FS_HZ;

                if (
                    recall_fastlock(
                        rx_lo,
                        tx_lo,
                        slot
                    ) < 0
                ) {
                    printf(
                        "[-] Fastlock recall failed: %d\n",
                        r
                    );
                    continue;
                }

                usleep(
                    RETUNE_DELAY_US
                );

                if (
                    read_rx(
                        rx_buf,
                        lb_i,
                        lb_q,
                        rc_i,
                        rc_q,
                        loop_raw,
                        rx_raw
                    ) < 0
                ) {
                    printf(
                        "[-] RX failed: %d\n",
                        r
                    );
                    continue;
                }

                extract_bb_phasors_neon(
                    loop_raw,
                    rx_raw,
                    mixers,
                    phasors
                );

                /*
                 * Convert the ten BB tones into absolute RF bins.
                 */
                for (
                    int k = 0;
                    k < NUM_BB_FREQS;
                    k++
                ) {
                    long long rf =
                        center
                        + bb_frequency(k);

                    if (
                        rf < FMIN_HZ ||
                        rf > FMAX_HZ
                    )
                        continue;

                    int index =
                        (int)(
                            (rf - FMIN_HZ)
                            / BB_SPACING_HZ
                        );

                    if (
                        index < 0 ||
                        index >= num_output_bins
                    )
                        continue;

                    sweep_data[
                        2 * index
                    ] =
                        phasors[2 * k];

                    sweep_data[
                        2 * index + 1
                    ] =
                        phasors[2 * k + 1];
                }
            }
        }

        if (
            send_sweep(
                sock,
                &dst,
                sweep_data,
                num_output_bins,
                sweep_id,
                &seq
            ) < 0
        ) {
            printf(
                "[-] UDP sweep send failed\n"
            );
        } else {
            printf(
                "[+] Sweep %u sent\n",
                sweep_id
            );
        }

        sweep_id++;
    }

    /*
     * Normally unreachable.
     */
    iio_buffer_destroy(rx_buf);
    iio_buffer_destroy(tx_buf);

    iio_context_destroy(ctx);

    free(rx_profiles);
    free(tx_profiles);

    free(mixers);
    free(loop_raw);
    free(rx_raw);
    free(sweep_data);

    close(sock);

    return 0;
}