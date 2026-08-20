#include <iio.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>
#include <unistd.h>
#include <string.h>
#include <time.h>


#define FS 20e6
#define BB_FREQ 100e3
#define LO_FREQ 2.4e9
#define BUFF_SIZE 200
#define TX_AMP 100
#define CHAN_BW 2e6
#define PI 3.141592653589793
#define TX2_PHASE_OFFSET 0.0 // In degrees
#define STEP_PAUSE_US 1

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

int main(void) {
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
    // iio_channel_attr_write(tx1_phy, "rf_port_select", "A");
    // iio_channel_attr_write_longlong(tx1_phy, "rf_bandwidth", CHAN_BW);
    // iio_channel_attr_write_longlong(tx1_phy, "sampling_frequency", (long long)FS);
    // iio_channel_enable(tx1_i);
    // iio_channel_enable(tx1_q);

    // TX Channel 2 Initialization
    iio_channel_attr_write(tx2_phy, "rf_port_select", "B");
    iio_channel_attr_write_longlong(tx2_phy, "rf_bandwidth", CHAN_BW);
    iio_channel_attr_write_longlong(tx2_phy, "sampling_frequency", (long long)FS);
    iio_channel_enable(tx2_i);
    iio_channel_enable(tx2_q);

    // Generate the Fastlock Profiles
    long long freqs[] = {
        2400000000LL, 2400100000LL, 2400200000LL, 2400300000LL,
        2400400000LL, 2400500000LL, 2400600000LL, 2400700000LL
    };

    char profiles[11][128];
    for (int i = 0; i < 8; i++) {
        iio_channel_attr_write_longlong(tx_lo, "frequency", freqs[i]);
        iio_channel_attr_write(tx_lo, "fastlock_store", "0");
        ssize_t len = iio_channel_attr_read(tx_lo, "fastlock_save", profiles[i], sizeof(profiles[i]) - 1);
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

    // int num = 0;
    // int num_freqs = sizeof(freqs) / sizeof(freqs[0]);

    for (int i = 0; i < 8; i++) {
        char load[128];
        snprintf(load, sizeof(load), "%d%s", i, strchr(profiles[i], ' '));

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

    // while (1)
    //     sleep(1);
    iio_context_destroy(ctx);
    return 0;
}