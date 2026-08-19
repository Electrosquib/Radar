#include <iio.h>
#include <stdint.h>
#include <math.h>
#include <stdio.h>
#include <unistd.h>

#define FS 2500000.0
#define BB_FREQ 100.0
#define LO_FREQ 2400000000LL
#define N 20500
#define AMP 300.0

int main(void) {
    struct iio_context *ctx = iio_create_local_context();
    if (!ctx) return 1;

    struct iio_device *phy = iio_context_find_device(ctx, "ad9361-phy");
    struct iio_device *tx = iio_context_find_device(ctx, "cf-ad9361-dds-core-lpc");

    if (!phy || !tx) return 1;

    struct iio_channel *tx_phy = iio_device_find_channel(phy, "voltage0", true);
    struct iio_channel *tx_lo = iio_device_find_channel(phy, "altvoltage1", true);
    struct iio_channel *tx_i = iio_device_find_channel(tx, "voltage0", true);
    struct iio_channel *tx_q = iio_device_find_channel(tx, "voltage1", true);

    if (!tx_phy || !tx_lo || !tx_i || !tx_q) return 1;

    iio_channel_attr_write(tx_phy, "rf_port_select", "A");
    iio_channel_attr_write_longlong(tx_phy, "rf_bandwidth", 1500000);
    iio_channel_attr_write_longlong(tx_phy, "sampling_frequency", (long long)FS);
    iio_channel_attr_write_longlong(tx_lo, "frequency", LO_FREQ);

    iio_channel_enable(tx_i);
    iio_channel_enable(tx_q);

    struct iio_buffer *buf = iio_device_create_buffer(tx, N, true);
    if (!buf) {
        perror("TX buffer");
        return 1;
    }

    char *p;
    char *end = iio_buffer_end(buf);
    ptrdiff_t step = iio_buffer_step(buf);
    int n = 0;

    for (p = iio_buffer_first(buf, tx_i); p < end; p += step) {
        double phase = 2.0 * 3.141592653589793 * BB_FREQ * n / FS;
        ((int16_t *)p)[0] = (int16_t)(AMP * cos(phase)) << 4;
        ((int16_t *)p)[1] = (int16_t)(AMP * sin(phase)) << 4;
        n++;
    }

    if (iio_buffer_push(buf) < 0) {
        perror("push");
        return 1;
    }

    printf("Transmitting at %.4f MHz\n", (LO_FREQ + BB_FREQ) / 1e6);

    while (1) sleep(1);
}