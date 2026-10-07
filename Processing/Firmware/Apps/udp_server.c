#include <arpa/inet.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arm_neon.h>
#include <stdint.h>
#include <iio.h>
#include <stdlib.h>
#include <stddef.h>
#include <math.h>
#include <unistd.h>
#include <time.h>

// UDP Config
#define PORT 5000
#define SAMPLES_PER_PACKET 360
#define MAGIC 0x49514441

// Radar Config
#define FS 20e6
#define BB_FREQ 100e3
#define FMIN 2.4e9
#define FMAX 2.7e9
#define BUFF_SIZE 200
#define TX_AMP 100
#define CHAN_BW 2e6
#define PI 3.141592653589793
#define TX2_PHASE_OFFSET 0.0 // In degrees
#define STEP_PAUSE_US 1
#define BUFFER_LEN 400

static const float mixer_real_pattern[20] = {
    2.000000f, -3.902113f, 4.793604f, -2.557537f,
    -2.459650f, 2.138181f, 5.000000f, -0.091322f,
    -0.891491f, -4.029672f, -2.029672f, -2.891491f,
    1.908678f, 3.000000f, 4.138181f, -4.459650f,
    -0.557537f, 2.793604f, -1.902113f, 0.000000f
};
float bb_mixer_real[BUFFER_LEN];

static const float mixer_imag_pattern[20] = {
    0.000000f, -0.618034f, 2.793604f, -5.520147f,
    4.138181f, 2.459650f, -1.273457f, -4.793604f,
    -3.824430f, -3.361763f, -3.361763f, -3.824430f,
    -4.793604f, -1.273457f, 2.459650f, 4.138181f,
    -5.520147f, 2.793604f, -0.618034f, 0.000000f
};
float bb_mixer_imag[BUFFER_LEN];

float schroeder_phase_array[10] = {
    0.0f,
    0.0f,
    -0.628319f,
    -1.884956f,
    -3.769911f,
    -6.283185f,
    -8.796459f,
    -11.938052f,
    -15.707963f,
    -20.106194f
};

static inline float hsum(float32x4_t v) {
    float32x2_t s = vadd_f32(vget_low_f32(v), vget_high_f32(v));
    s = vpadd_f32(s, s);
    return vget_lane_f32(s, 0);
}


int create_fastlock_profiles(double start_freq, double bw, double step) {
    unsigned int num_steps = (unsigned int)(bw / step);
    double *freqs = (double*)malloc(num_steps * sizeof(double));
    if (freqs == NULL) {
        printf("[-] Insufficient memory to build frequency list");
        return 1;
    }
    for (unsigned int i = 0; i < num_steps; i ++) {
        freqs[i] = start_freq + i * step;
    };

    return 0;
}


void extract_bb_phasors_neon(
    const float *loop_raw,
    const float *rx_raw,
    const float *bb_mixers,
    int buff_size,
    int capture_averages,
    int num_freqs,
    float *out
) {
    int mini_buff = buff_size / capture_averages;

    float numerator_re[num_freqs];
    float numerator_im[num_freqs];
    float denominator[num_freqs];

    for (int k = 0; k < num_freqs; k++) {
        numerator_re[k] = 0.0f;
        numerator_im[k] = 0.0f;
        denominator[k] = 0.0f;
    }

    loop_raw += 2 * mini_buff;
    rx_raw += 2 * mini_buff;

    for (int i = 0; i < capture_averages; i++) {
        int a = i * mini_buff;

        for (int k = 0; k < num_freqs; k++) {
            float32x4_t lr_acc = vdupq_n_f32(0.0f);
            float32x4_t li_acc = vdupq_n_f32(0.0f);
            float32x4_t rr_acc = vdupq_n_f32(0.0f);
            float32x4_t ri_acc = vdupq_n_f32(0.0f);

            const float *m = bb_mixers + 2 * (k * buff_size + a);
            const float *l = loop_raw + 2 * a;
            const float *r = rx_raw + 2 * a;

            for (int n = 0; n < mini_buff; n += 4) {
                float32x4x2_t mv = vld2q_f32(m + 2 * n);
                float32x4x2_t lv = vld2q_f32(l + 2 * n);
                float32x4x2_t rv = vld2q_f32(r + 2 * n);

                lr_acc = vmlsq_f32(lr_acc, mv.val[1], lv.val[1]);
                lr_acc = vmlaq_f32(lr_acc, mv.val[0], lv.val[0]);

                li_acc = vmlaq_f32(li_acc, mv.val[0], lv.val[1]);
                li_acc = vmlaq_f32(li_acc, mv.val[1], lv.val[0]);

                rr_acc = vmlsq_f32(rr_acc, mv.val[1], rv.val[1]);
                rr_acc = vmlaq_f32(rr_acc, mv.val[0], rv.val[0]);

                ri_acc = vmlaq_f32(ri_acc, mv.val[0], rv.val[1]);
                ri_acc = vmlaq_f32(ri_acc, mv.val[1], rv.val[0]);
            }

            float scale = 1.0f / mini_buff;

            float lr = hsum(lr_acc) * scale;
            float li = hsum(li_acc) * scale;
            float rr = hsum(rr_acc) * scale;
            float ri = hsum(ri_acc) * scale;

            numerator_re[k] += rr * lr + ri * li;
            numerator_im[k] += ri * lr - rr * li;
            denominator[k] += lr * lr + li * li;
        }
    }

    for (int k = 0; k < num_freqs; k++) {
        float d = denominator[k] + 1e-12f;
        out[2 * k] = numerator_re[k] / d;
        out[2 * k + 1] = numerator_im[k] / d;
    }
}


typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint32_t seq;
    uint32_t sweep;
    uint16_t tone;
    uint16_t samples;
} packet_header_t;



typedef struct {
    int16_t i;
    int16_t q;
} iq_t;



int main() {
    // Mixer Vectors
    for (int i = 0; i < BUFFER_LEN; i++) {
        bb_mixer_real[i] = mixer_real_pattern[i % 20];
        bb_mixer_imag[i] = mixer_imag_pattern[i % 20];
    }

    // UDP Stuff
    // -------------------------------------------------------------------------
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    int sndbuf = 4 * 1024 * 1024;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf));
    struct sockaddr_in dst = {
        .sin_family = AF_INET,
        .sin_port = htons(PORT)
    };
    inet_pton(AF_INET, "192.168.2.10", &dst.sin_addr);
    uint8_t packet[sizeof(packet_header_t) + SAMPLES_PER_PACKET * sizeof(iq_t)];
    uint32_t seq = 0;
    iq_t iq_buffer[1024];


    // AD936X Stuff
    // -------------------------------------------------------------------------

    struct iio_context *ctx = iio_create_local_context();
    if (!ctx) {
        printf("[-] local context could not be created\n");
        return 1;
    }
    struct iio_device *sdr = iio_context_find_device(ctx, "ad9361-phy");
    if (!sdr) {
        printf("[-] ad9361-phy not found\n");
        return 1;
    }
    struct iio_device *tx = iio_context_find_device(ctx, "cf-ad9361-dds-core-lpc");
    if (!tx) {
        printf("[-] TX channel not found\n");
        return 1;
    }
    struct iio_device *rx = iio_context_find_device(ctx, "cf-ad9361-lpc");
    if (!rx) {
        printf("[-] RX channel not found\n");
        return 1;
    }

    //  TX/RX Local Oscillators
    struct iio_channel *tx_lo = iio_device_find_channel(sdr, "altvoltage1", true);
    struct iio_channel *rx_lo = iio_device_find_channel(sdr, "altvoltage0", true);

    // RX Channel 1
    struct iio_channel *rx1_phy = iio_device_find_channel(sdr, "voltage0", false);
    struct iio_channel *rx1_i = iio_device_find_channel(rx, "voltage0", false);
    struct iio_channel *rx1_q = iio_device_find_channel(rx, "voltage1", false);

    // RX Channel 2
    struct iio_channel *rx2_phy = iio_device_find_channel(sdr, "voltage1", false);
    struct iio_channel *rx2_i = iio_device_find_channel(rx, "voltage2", false);
    struct iio_channel *rx2_q = iio_device_find_channel(rx, "voltage3", false);

    // TX Channel 1
    struct iio_channel *tx1_phy = iio_device_find_channel(sdr, "voltage0", true);
    struct iio_channel *tx1_i = iio_device_find_channel(tx, "voltage0", true);
    struct iio_channel *tx1_q = iio_device_find_channel(tx, "voltage1", true);
    
    // TX Channel 2
    struct iio_channel *tx2_phy = iio_device_find_channel(sdr, "voltage1", true);
    struct iio_channel *tx2_i = iio_device_find_channel(tx, "voltage2", true);
    struct iio_channel *tx2_q = iio_device_find_channel(tx, "voltage3", true);

    // Validate Channels
    if (!tx_lo || !rx_lo || !rx1_phy || !rx1_i || !rx1_q || !rx2_phy || !rx2_i || !rx2_q || !tx1_phy || !tx1_i || !tx1_q || !tx2_phy || !tx2_i || !tx2_q) {
        printf("[-] One or more SDR channels not found\n");
        return 1;
    }

    // Device Logging
    unsigned int num_channels = iio_device_get_channels_count(sdr);
    printf("Using Device: %s\n", iio_device_get_name(sdr));
    for (unsigned int i = 0; i < num_channels; i++) {
        struct iio_channel *channel = iio_device_get_channel(sdr, i);
        const char *name = iio_channel_get_name(channel);
        if (name != NULL) {
            printf("\t- Channel %u: %s\n", i, name);   
        }
    }

    int steps = create_fastlock_profiles(2.4e9, 300e6, 10e6);
    printf("Steps: %u\n", steps);

    // TX Channel 1 Initialization
    iio_channel_attr_write(tx1_phy, "rf_port_select", "A");
    iio_channel_attr_write_longlong(tx1_phy, "rf_bandwidth", CHAN_BW);
    iio_channel_attr_write_longlong(tx1_phy, "sampling_frequency", (long long)FS);
    iio_channel_enable(tx1_i);
    iio_channel_enable(tx1_q);

    // TX Channel 2 Initialization
    iio_channel_attr_write(tx2_phy, "rf_port_select", "B");
    iio_channel_attr_write_longlong(tx2_phy, "rf_bandwidth", CHAN_BW);
    iio_channel_attr_write_longlong(tx2_phy, "sampling_frequency", (long long)FS);
    iio_channel_enable(tx2_i);
    iio_channel_enable(tx2_q);

    // Loopback RX Channel Initialization
    iio_channel_attr_write(rx1_phy, "rf_port_select", "A_BALANCED");
    iio_channel_attr_write_longlong(rx1_phy, "rf_bandwidth", CHAN_BW);
    iio_channel_attr_write_longlong(rx1_phy, "sampling_frequency", (long long)FS);
    iio_channel_enable(rx1_i);
    iio_channel_enable(rx1_q);

    // Receive RX Channel Initialization
    iio_channel_attr_write(rx2_phy, "rf_port_select", "B_BALANCED");
    iio_channel_attr_write_longlong(rx2_phy, "rf_bandwidth", CHAN_BW);
    iio_channel_attr_write_longlong(rx2_phy, "sampling_frequency", (long long)FS);
    iio_channel_enable(rx2_i);
    iio_channel_enable(rx2_q);

    // Generate the Fastlock Profiles
    int num_freqs = (int)((FMAX - FMIN) / FS);
    long long FREQS[num_freqs];
    for (int i = 0; i < num_freqs; i++)
        FREQS[i] = FMIN + i * FS + FS / 2;
    char profiles[8][128];
    int batch_size = num_freqs < 8 ? num_freqs : 8;
    for (int i = 0; i < batch_size; i++) {
        iio_channel_attr_write_longlong(tx_lo, "frequency", FREQS[i]);
        iio_channel_attr_write(tx_lo, "fastlock_store", "0");
        ssize_t len = iio_channel_attr_read(
            tx_lo,
            "fastlock_save",
            profiles[i],
            sizeof(profiles[i]) - 1
        );
        if (len < 0) {
            printf("[-] Failed saving profile %d\n", i);
            return 1;
        }
        profiles[i][len] = '\0';
    }


    // Create TX Buffer
    struct iio_buffer *tx_buf = iio_device_create_buffer(tx, BUFF_SIZE, true);
    if (!tx_buf) {
        printf("[-] TX buffer couldn't be created");
        return 1;
    }

    // Populate The TX Buffer
    // Buffer structure: T1I0 T1Q0 T2I0 T2Q0 ... 
    // First byte is on tx1_i channel
    // Ae^j(2pift + phi) = Acos(2pift + phi) + jAsin(2pift + phi),  t = n/fs

    ptrdiff_t step = iio_buffer_step(tx_buf);
    char *p1i = iio_buffer_first(tx_buf, tx1_i);
    char *p1q = iio_buffer_first(tx_buf, tx1_q);
    char *p2i = iio_buffer_first(tx_buf, tx2_i);
    char *p2q = iio_buffer_first(tx_buf, tx2_q);

    for (size_t n = 0; n < BUFF_SIZE; n++) {
        double phase1 = 2.0 * PI * BB_FREQ * n / FS;
        double phase2 = phase1 + TX2_PHASE_OFFSET * PI / 180.0;

        *(int16_t *)p1i = (int16_t)(TX_AMP * cos(phase1) * 16.0);
        *(int16_t *)p1q = (int16_t)(TX_AMP * sin(phase1) * 16.0);

        *(int16_t *)p2i = (int16_t)(TX_AMP * cos(phase2) * 16.0);
        *(int16_t *)p2q = (int16_t)(TX_AMP * sin(phase2) * 16.0);

        p1i += step;
        p1q += step;
        p2i += step;
        p2q += step;
    }

    // Start the TX buffer
    if (iio_buffer_push(tx_buf) < 0) {
        printf("[-] Error pushing TX buffer");
        return 1;
    }

    for (int i = 0; i < 8; i++) {
        char load[128];
        snprintf(load, sizeof(load), "%d%s", i, strchr(profiles[i], ' '));
        usleep(1000);
        if (iio_channel_attr_write(tx_lo, "fastlock_load", load) < 0)
            printf("Failed loading slot %d\n", i);
    }

    if (iio_device_debug_attr_write_bool(
        sdr,
        "adi,tx-fastlock-pincontrol-enable",
        true
    ) < 0)
        printf("Failed enabling TX pin control\n");

    if (iio_channel_attr_write(tx_lo, "fastlock_recall", "0") < 0)
        printf("Failed initial recall\n");

    printf("[+] FPGA fastlock pin control active\n");


    while (1) {
        int num_samples = 1024;

        for (int offset = 0; offset < num_samples; offset += SAMPLES_PER_PACKET) {
            int count = num_samples - offset;

            if (count > SAMPLES_PER_PACKET)
                count = SAMPLES_PER_PACKET;

            packet_header_t header = {
                .magic = htonl(MAGIC),
                .seq = htonl(seq++),
                .sweep = htonl(0),
                .tone = htons(0),
                .samples = htons(count)
            };

            memcpy(packet, &header, sizeof(header));
            memcpy(packet + sizeof(header), &iq_buffer[offset], count * sizeof(iq_t));

            sendto(
                sock,
                packet,
                sizeof(header) + count * sizeof(iq_t),
                0,
                (struct sockaddr *)&dst,
                sizeof(dst)
            );
        }
    }

    
    iio_context_destroy(ctx);
    return 0;
}