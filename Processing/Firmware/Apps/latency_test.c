#include <iio.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define N_TESTS 1000

static double elapsed_us(struct timespec a, struct timespec b) {
    return (b.tv_sec - a.tv_sec) * 1e6 + (b.tv_nsec - a.tv_nsec) / 1e3;
}

int main(void) {
    struct iio_context *ctx = iio_create_local_context();
    if (!ctx) return 1;

    struct iio_device *phy = iio_context_find_device(ctx, "ad9361-phy");
    struct iio_channel *tx_lo = phy ? iio_device_find_channel(phy, "altvoltage1", true) : NULL;
    if (!tx_lo) return 1;

    long long freqs[8] = {
        2400000000LL, 2400100000LL, 2400200000LL, 2400300000LL,
        2400400000LL, 2400500000LL, 2400600000LL, 2400700000LL
    };

    char profiles[8][128];
    char loads[8][128];
    char slots[8][2];

    for (int i = 0; i < 8; i++) {
        iio_channel_attr_write_longlong(tx_lo, "frequency", freqs[i]);
        iio_channel_attr_write(tx_lo, "fastlock_store", "0");

        ssize_t len = iio_channel_attr_read(tx_lo, "fastlock_save", profiles[i], sizeof(profiles[i]) - 1);
        if (len < 0) return 1;
        profiles[i][len] = '\0';

        char *data = strchr(profiles[i], ' ');
        if (!data) return 1;

        snprintf(loads[i], sizeof(loads[i]), "%d%s", i, data);
        snprintf(slots[i], sizeof(slots[i]), "%d", i);
    }

    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int n = 0; n < N_TESTS; n++) {
        if (iio_channel_attr_write(tx_lo, "fastlock_load", loads[n & 7]) < 0)
            return 1;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);

    printf("Fastlock load:   %.2f us/call\n",
           elapsed_us(start, end) / N_TESTS);

    for (int i = 0; i < 8; i++) {
        if (iio_channel_attr_write(tx_lo, "fastlock_load", loads[i]) < 0)
            return 1;
    }

    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int n = 0; n < N_TESTS; n++) {
        if (iio_channel_attr_write(tx_lo, "fastlock_recall", slots[n & 7]) < 0)
            return 1;
    }
    clock_gettime(CLOCK_MONOTONIC, &end);

    printf("Fastlock recall: %.2f us/call\n",
           elapsed_us(start, end) / N_TESTS);

    iio_context_destroy(ctx);
    return 0;
}