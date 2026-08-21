#include <iio.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main(void) {
long long freqs[] = {
    3070000000LL,
    3060000000LL,
    3050000000LL,
    3040000000LL,
    3030000000LL,
    3020000000LL,
    3010000000LL,
    3000000000LL
};

    int num_freqs = sizeof(freqs) / sizeof(freqs[0]);
    char profiles[8][128];

    struct iio_context *ctx = iio_create_local_context();
    if (!ctx) {
        printf("Failed to create context\n");
        return 1;
    }

    struct iio_device *sdr = iio_context_find_device(ctx, "ad9361-phy");
    if (!sdr) {
        printf("ad9361-phy not found\n");
        return 1;
    }

    struct iio_channel *tx_lo = iio_device_find_channel(sdr, "altvoltage1", true);
    if (!tx_lo) {
        printf("TX LO not found\n");
        return 1;
    }

    if (iio_device_debug_attr_write_bool(
        sdr,
        "adi,tx-fastlock-pincontrol-enable",
        false
    ) < 0) {
        printf("Failed disabling GPIO fastlock control\n");
        return 1;
    }

    printf("GPIO fastlock control disabled\n");

    for (int i = 0; i < num_freqs; i++) {
        if (iio_channel_attr_write_longlong(
            tx_lo,
            "frequency",
            freqs[i]
        ) < 0) {
            printf("Failed setting frequency %d\n", i);
            return 1;
        }

        if (iio_channel_attr_write(
            tx_lo,
            "fastlock_store",
            "0"
        ) < 0) {
            printf("Failed storing temporary profile %d\n", i);
            return 1;
        }

        ssize_t len = iio_channel_attr_read(
            tx_lo,
            "fastlock_save",
            profiles[i],
            sizeof(profiles[i]) - 1
        );

        if (len < 0) {
            printf("Failed saving profile %d\n", i);
            return 1;
        }

        profiles[i][len] = '\0';

        char *data = strchr(profiles[i], ' ');
        if (!data) {
            printf("Invalid profile data: %s\n", profiles[i]);
            return 1;
        }

        char load[128];
        snprintf(load, sizeof(load), "%d%s", i, data);

        if (iio_channel_attr_write(
            tx_lo,
            "fastlock_load",
            load
        ) < 0) {
            printf("Failed loading slot %d\n", i);
            return 1;
        }

        printf("Slot %d loaded: %.3f GHz\n",
            i,
            freqs[i] / 1e9
        );
    }

    printf("\nCycling profiles once per second...\n");

    while (1) {
        for (int slot = 0; slot < num_freqs; slot++) {
            char value[4];
            snprintf(value, sizeof(value), "%d", slot);

            if (iio_channel_attr_write(
                tx_lo,
                "fastlock_recall",
                value
            ) < 0) {
                printf("Failed recalling slot %d\n", slot);
                return 1;
            }

            printf("Slot %d -> %.3f GHz\n",
                slot,
                freqs[slot] / 1e9
            );

            sleep(1);
        }
    }
}