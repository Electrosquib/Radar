#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <iio.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <time.h>
#include <unistd.h>

#define PROTOCOL_VERSION 1u
#define MAGIC "SFCW"
#define FASTLOCK_SLOTS 8u
#define PROFILE_SIZE 128u
#define PI 3.14159265358979323846
#define FLAG_SCHROEDER 0x1u
#define FLAG_TIMINGS 0x2u
#define MAX_RETUNES 4096u
#define MAX_BUFFER_SAMPLES (1u << 20)
#define MAX_CAPTURE_BYTES (512u * 1024u * 1024u)

enum message_type { MSG_CONFIGURE = 1, MSG_SWEEP = 2, MSG_PING = 3, MSG_SHUTDOWN = 4 };
enum timing_operation {
    TIMING_FULL_RETUNE = 1, TIMING_FASTLOCK_STORE = 2,
    TIMING_FASTLOCK_SAVE = 3, TIMING_FASTLOCK_LOAD = 4,
    TIMING_FASTLOCK_RECALL = 5, TIMING_BUFFER_REFILL = 6,
};
enum timing_side { SIDE_NONE = 0, SIDE_RX = 1, SIDE_TX = 2 };

#pragma pack(push, 1)
struct message_header {
    char magic[4];
    uint16_t version;
    uint16_t type;
    uint32_t status;
    uint64_t payload_len;
};
struct wire_config {
    uint32_t flags, sample_rate, rf_bandwidth, buffer_size;
    uint32_t capture_averages, retune_delay_us, num_retunes;
    uint32_t rx_signal_port, rx_loopback_port, tx_signal_port, tx_loopback_port;
    int32_t rx_gain_db, loopback_gain_db, tx_gain_db;
    double tx_loopback_gain_db, bb_spacing_hz, bb_gain, tx_bb_scale, phase_offset_rad;
};
struct timing_record {
    uint16_t operation;
    uint8_t side, slot;
    uint32_t frequency_index, detail;
    int32_t status;
    uint64_t duration_ns;
};
struct sweep_prefix {
    uint32_t num_retunes, capture_averages, buffer_size, channel_count, timing_count;
    uint64_t acquisition_ns;
};
#pragma pack(pop)

typedef char assert_header_size[(sizeof(struct message_header) == 20) ? 1 : -1];
typedef char assert_config_size[(sizeof(struct wire_config) == 96) ? 1 : -1];
typedef char assert_timing_size[(sizeof(struct timing_record) == 24) ? 1 : -1];
typedef char assert_sweep_prefix_size[(sizeof(struct sweep_prefix) == 28) ? 1 : -1];

struct timing_vector {
    struct timing_record *items;
    size_t count, capacity;
};
struct controller {
    struct wire_config cfg;
    uint64_t *frequencies;
    char (*rx_profiles)[PROFILE_SIZE], (*tx_profiles)[PROFILE_SIZE];
    struct iio_context *ctx;
    struct iio_device *phy, *rx, *tx;
    struct iio_channel *rx_lo, *tx_lo;
    struct iio_channel *rx_phy[2], *tx_phy[2];
    struct iio_channel *rx_i[2], *rx_q[2], *tx_i[2], *tx_q[2];
    struct iio_buffer *rx_buffer, *tx_buffer;
    bool configured;
};

static uint64_t monotonic_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}
static int read_full(void *buffer, size_t length) {
    uint8_t *cursor = buffer;
    while (length) {
        ssize_t count = read(STDIN_FILENO, cursor, length);
        if (count == 0) return 0;
        if (count < 0) { if (errno == EINTR) continue; return -1; }
        cursor += count; length -= (size_t)count;
    }
    return 1;
}
static int write_full(const void *buffer, size_t length) {
    const uint8_t *cursor = buffer;
    while (length) {
        ssize_t count = write(STDOUT_FILENO, cursor, length);
        if (count < 0) { if (errno == EINTR) continue; return -1; }
        cursor += count; length -= (size_t)count;
    }
    return 0;
}
static int send_response(uint16_t type, uint32_t status, const void *payload, uint64_t length) {
    struct message_header header;
    memcpy(header.magic, MAGIC, 4);
    header.version = PROTOCOL_VERSION; header.type = type;
    header.status = status; header.payload_len = length;
    if (write_full(&header, sizeof(header)) < 0) return -1;
    return length ? write_full(payload, (size_t)length) : 0;
}
static int send_error(uint16_t type, const char *message) {
    fprintf(stderr, "SFCW error: %s\n", message);
    return send_response(type, 1u, message, strlen(message));
}
static void timing_clear(struct timing_vector *v) { free(v->items); memset(v, 0, sizeof(*v)); }
static int timing_append(struct timing_vector *v, bool enabled, uint16_t operation,
                         uint8_t side, uint8_t slot, uint32_t index, uint32_t detail,
                         int status, uint64_t started) {
    if (!enabled) return 0;
    if (v->count == v->capacity) {
        size_t capacity = v->capacity ? v->capacity * 2u : 64u;
        struct timing_record *items = realloc(v->items, capacity * sizeof(*items));
        if (!items) return -1;
        v->items = items; v->capacity = capacity;
    }
    v->items[v->count++] = (struct timing_record) {
        operation, side, slot, index, detail, status, monotonic_ns() - started
    };
    return 0;
}
static void controller_cleanup(struct controller *c) {
    if (c->rx_buffer) iio_buffer_destroy(c->rx_buffer);
    if (c->tx_buffer) iio_buffer_destroy(c->tx_buffer);
    if (c->ctx) iio_context_destroy(c->ctx);
    free(c->frequencies); free(c->rx_profiles); free(c->tx_profiles);
    memset(c, 0, sizeof(*c));
}
static int write_attr(struct iio_channel *ch, const char *name, const char *value) {
    return iio_channel_attr_write(ch, name, value) < 0 ? -1 : 0;
}
static int write_attr_ll(struct iio_channel *ch, const char *name, long long value) {
    return iio_channel_attr_write_longlong(ch, name, value) < 0 ? -1 : 0;
}
static int write_gain(struct iio_channel *ch, double gain) {
    char value[32]; snprintf(value, sizeof(value), "%.2f", gain);
    return write_attr(ch, "hardwaregain", value);
}
static int sleep_us(uint32_t delay) {
    struct timespec request = { delay / 1000000u, (long)(delay % 1000000u) * 1000l };
    while (nanosleep(&request, &request) < 0) if (errno != EINTR) return -1;
    return 0;
}
static int validate_config(const struct wire_config *cfg, char *error, size_t size) {
    uint64_t bytes;
    double tones;
    if (!cfg->sample_rate || !cfg->rf_bandwidth || !cfg->buffer_size ||
        !cfg->capture_averages || !cfg->num_retunes) {
        snprintf(error, size, "sample rate, bandwidth, buffer, averages, and retunes must be nonzero"); return -1;
    }
    if (cfg->num_retunes > MAX_RETUNES || cfg->buffer_size > MAX_BUFFER_SAMPLES) {
        snprintf(error, size, "configuration exceeds controller limits"); return -1;
    }
    if (cfg->rx_signal_port > 1 || cfg->rx_loopback_port > 1 ||
        cfg->tx_signal_port > 1 || cfg->tx_loopback_port > 1 ||
        cfg->rx_signal_port == cfg->rx_loopback_port ||
        cfg->tx_signal_port == cfg->tx_loopback_port) {
        snprintf(error, size, "RX and TX ports must each be distinct channel indices 0 and 1"); return -1;
    }
    if (!(cfg->bb_spacing_hz > 0.0) || !isfinite(cfg->bb_spacing_hz) ||
        !isfinite(cfg->bb_gain) || !isfinite(cfg->tx_bb_scale) || !isfinite(cfg->phase_offset_rad)) {
        snprintf(error, size, "invalid baseband configuration"); return -1;
    }
    tones = (double)cfg->sample_rate / cfg->bb_spacing_hz;
    if (tones < 1.0 || fabs(tones - round(tones)) > 1e-9) {
        snprintf(error, size, "sample rate must be an integer multiple of baseband spacing"); return -1;
    }
    bytes = (uint64_t)cfg->num_retunes * cfg->capture_averages * cfg->buffer_size * 8u;
    if (bytes > MAX_CAPTURE_BYTES) { snprintf(error, size, "requested raw sweep exceeds 512 MiB"); return -1; }
    return 0;
}
static int find_hardware(struct controller *c, char *error, size_t size) {
    unsigned int port;
    c->ctx = iio_create_local_context();
    if (!c->ctx) { snprintf(error, size, "could not create local IIO context"); return -1; }
    c->phy = iio_context_find_device(c->ctx, "ad9361-phy");
    c->rx = iio_context_find_device(c->ctx, "cf-ad9361-lpc");
    c->tx = iio_context_find_device(c->ctx, "cf-ad9361-dds-core-lpc");
    if (!c->phy || !c->rx || !c->tx) { snprintf(error, size, "required AD9361 IIO devices were not found"); return -1; }
    c->rx_lo = iio_device_find_channel(c->phy, "altvoltage0", true);
    c->tx_lo = iio_device_find_channel(c->phy, "altvoltage1", true);
    for (port = 0; port < 2; ++port) {
        char name[16];
        snprintf(name, sizeof(name), "voltage%u", port);
        c->rx_phy[port] = iio_device_find_channel(c->phy, name, false);
        c->tx_phy[port] = iio_device_find_channel(c->phy, name, true);
        snprintf(name, sizeof(name), "voltage%u", port * 2u);
        c->rx_i[port] = iio_device_find_channel(c->rx, name, false);
        c->tx_i[port] = iio_device_find_channel(c->tx, name, true);
        snprintf(name, sizeof(name), "voltage%u", port * 2u + 1u);
        c->rx_q[port] = iio_device_find_channel(c->rx, name, false);
        c->tx_q[port] = iio_device_find_channel(c->tx, name, true);
        if (!c->rx_phy[port] || !c->tx_phy[port] || !c->rx_i[port] || !c->rx_q[port] ||
            !c->tx_i[port] || !c->tx_q[port]) {
            snprintf(error, size, "required AD9361 channel %u was not found", port); return -1;
        }
    }
    if (!c->rx_lo || !c->tx_lo) { snprintf(error, size, "AD9361 RX/TX LO channels were not found"); return -1; }
    return 0;
}
static int configure_channels(struct controller *c, char *error, size_t size) {
    unsigned int port;
    for (port = 0; port < 2; ++port) {
        if (write_attr_ll(c->rx_phy[port], "rf_bandwidth", c->cfg.rf_bandwidth) ||
            write_attr_ll(c->rx_phy[port], "sampling_frequency", c->cfg.sample_rate) ||
            write_attr(c->rx_phy[port], "gain_control_mode", "manual") ||
            write_attr_ll(c->tx_phy[port], "rf_bandwidth", c->cfg.rf_bandwidth) ||
            write_attr_ll(c->tx_phy[port], "sampling_frequency", c->cfg.sample_rate)) {
            snprintf(error, size, "failed configuring physical channel %u", port); return -1;
        }
        iio_channel_enable(c->rx_i[port]); iio_channel_enable(c->rx_q[port]);
        iio_channel_enable(c->tx_i[port]); iio_channel_enable(c->tx_q[port]);
    }
    if (write_gain(c->rx_phy[c->cfg.rx_signal_port], c->cfg.rx_gain_db) ||
        write_gain(c->rx_phy[c->cfg.rx_loopback_port], c->cfg.loopback_gain_db) ||
        write_gain(c->tx_phy[c->cfg.tx_signal_port], c->cfg.tx_gain_db) ||
        write_gain(c->tx_phy[c->cfg.tx_loopback_port], c->cfg.tx_loopback_gain_db)) {
        snprintf(error, size, "failed configuring manual gains"); return -1;
    }
    return 0;
}
static int16_t clamp_i16(double value) {
    if (value > 32767.0) return 32767;
    if (value < -32768.0) return -32768;
    return (int16_t)lrint(value);
}
static int create_tx_buffer(struct controller *c, char *error, size_t size) {
    ptrdiff_t step;
    char *ip[2], *qp[2];
    uint32_t sample, tone, tones, port;
    double scale;
    c->tx_buffer = iio_device_create_buffer(c->tx, c->cfg.buffer_size, true);
    if (!c->tx_buffer) { snprintf(error, size, "could not create cyclic TX buffer"); return -1; }
    step = iio_buffer_step(c->tx_buffer);
    for (port = 0; port < 2; ++port) {
        ip[port] = iio_buffer_first(c->tx_buffer, c->tx_i[port]);
        qp[port] = iio_buffer_first(c->tx_buffer, c->tx_q[port]);
    }
    tones = (uint32_t)llround((double)c->cfg.sample_rate / c->cfg.bb_spacing_hz);
    scale = c->cfg.bb_gain * c->cfg.tx_bb_scale / tones;
    for (sample = 0; sample < c->cfg.buffer_size; ++sample) {
        double iv = 0.0, qv = 0.0;
        for (tone = 0; tone < tones; ++tone) {
            double frequency = -(double)c->cfg.sample_rate / 2.0 + tone * c->cfg.bb_spacing_hz;
            double phase = c->cfg.phase_offset_rad;
            if (c->cfg.flags & FLAG_SCHROEDER) phase -= PI * tone * (tone - 1.0) / tones;
            phase += 2.0 * PI * frequency * sample / c->cfg.sample_rate;
            iv += cos(phase); qv += sin(phase);
        }
        for (port = 0; port < 2; ++port) {
            *(int16_t *)ip[port] = clamp_i16(iv * scale);
            *(int16_t *)qp[port] = clamp_i16(qv * scale);
            ip[port] += step; qp[port] += step;
        }
    }
    if (iio_buffer_push(c->tx_buffer) < 0) { snprintf(error, size, "failed pushing cyclic TX buffer"); return -1; }
    return 0;
}
static int timed_frequency_write(struct iio_channel *lo, uint64_t frequency,
                                  struct timing_vector *timings, bool timings_enabled,
                                  uint8_t side, uint32_t index) {
    uint64_t started = monotonic_ns();
    int status = write_attr_ll(lo, "frequency", (long long)frequency);
    if (timing_append(timings, timings_enabled, TIMING_FULL_RETUNE, side, 255u, index, 0u, status, started) < 0) return -2;
    return status;
}
static int save_profile(struct iio_channel *lo, char *profile, struct timing_vector *timings,
                         bool timings_enabled, uint8_t side, uint32_t index) {
    uint64_t started = monotonic_ns();
    int status = write_attr(lo, "fastlock_store", "0");
    ssize_t length;
    if (timing_append(timings, timings_enabled, TIMING_FASTLOCK_STORE, side, 0u, index, 0u, status, started) < 0) return -2;
    if (status < 0) return -1;
    started = monotonic_ns();
    length = iio_channel_attr_read(lo, "fastlock_save", profile, PROFILE_SIZE - 1u);
    status = length < 0 ? -1 : 0;
    if (timing_append(timings, timings_enabled, TIMING_FASTLOCK_SAVE, side, 0u, index, 0u, status, started) < 0) return -2;
    if (length < 0) return -1;
    profile[length] = '\0';
    return strchr(profile, ' ') ? 0 : -1;
}
static int create_profiles(struct controller *c, struct timing_vector *timings, char *error, size_t size) {
    uint32_t index;
    bool timings_enabled = (c->cfg.flags & FLAG_TIMINGS) != 0;
    for (index = 0; index < c->cfg.num_retunes; ++index) {
        if (timed_frequency_write(c->rx_lo, c->frequencies[index], timings, timings_enabled, SIDE_RX, index) ||
            timed_frequency_write(c->tx_lo, c->frequencies[index], timings, timings_enabled, SIDE_TX, index) ||
            save_profile(c->rx_lo, c->rx_profiles[index], timings, timings_enabled, SIDE_RX, index) ||
            save_profile(c->tx_lo, c->tx_profiles[index], timings, timings_enabled, SIDE_TX, index)) {
            snprintf(error, size, "failed generating fastlock profile %u", index); return -1;
        }
    }
    return 0;
}
static int configure_controller(struct controller *c, const uint8_t *payload, size_t payload_len,
                                struct timing_vector *timings, char *error, size_t size) {
    struct wire_config cfg;
    size_t expected;
    uint32_t index;
    if (payload_len < sizeof(cfg)) { snprintf(error, size, "configure payload is truncated"); return -1; }
    memcpy(&cfg, payload, sizeof(cfg));
    expected = sizeof(cfg) + (size_t)cfg.num_retunes * sizeof(uint64_t);
    if (payload_len != expected || validate_config(&cfg, error, size) < 0) return -1;
    controller_cleanup(c); c->cfg = cfg;
    c->frequencies = calloc(cfg.num_retunes, sizeof(*c->frequencies));
    c->rx_profiles = calloc(cfg.num_retunes, sizeof(*c->rx_profiles));
    c->tx_profiles = calloc(cfg.num_retunes, sizeof(*c->tx_profiles));
    if (!c->frequencies || !c->rx_profiles || !c->tx_profiles) { snprintf(error, size, "out of memory allocating configuration"); goto fail; }
    memcpy(c->frequencies, payload + sizeof(cfg), cfg.num_retunes * sizeof(*c->frequencies));
    for (index = 0; index < cfg.num_retunes; ++index) {
        if (c->frequencies[index] < 70000000ull || c->frequencies[index] > 6000000000ull) {
            snprintf(error, size, "frequency %u is outside AD9361 limits", index); goto fail;
        }
    }
    if (find_hardware(c, error, size) || configure_channels(c, error, size) ||
        create_profiles(c, timings, error, size) || create_tx_buffer(c, error, size)) goto fail;
    c->rx_buffer = iio_device_create_buffer(c->rx, cfg.buffer_size, false);
    if (!c->rx_buffer) { snprintf(error, size, "could not create RX buffer"); goto fail; }
    c->configured = true; return 0;
fail:
    controller_cleanup(c); return -1;
}
static int load_profile(struct iio_channel *lo, const char *profile, uint32_t slot,
                         struct timing_vector *timings, bool timings_enabled, uint8_t side, uint32_t index) {
    char value[PROFILE_SIZE];
    const char *data = strchr(profile, ' ');
    uint64_t started;
    int status;
    if (!data) return -1;
    snprintf(value, sizeof(value), "%u%s", slot, data);
    started = monotonic_ns(); status = write_attr(lo, "fastlock_load", value);
    if (timing_append(timings, timings_enabled, TIMING_FASTLOCK_LOAD, side, (uint8_t)slot, index, 0u, status, started) < 0) return -2;
    return status;
}
static int recall_profile(struct iio_channel *lo, uint32_t slot, struct timing_vector *timings,
                           bool timings_enabled, uint8_t side, uint32_t index) {
    char value[4]; uint64_t started; int status;
    snprintf(value, sizeof(value), "%u", slot);
    started = monotonic_ns(); status = write_attr(lo, "fastlock_recall", value);
    if (timing_append(timings, timings_enabled, TIMING_FASTLOCK_RECALL, side, (uint8_t)slot, index, 0u, status, started) < 0) return -2;
    return status;
}
static int capture_sweep(struct controller *c, int16_t *raw, struct timing_vector *timings,
                         uint64_t *acquisition_ns, char *error, size_t size) {
    uint32_t group, index, slot, average, sample, port;
    bool timings_enabled = (c->cfg.flags & FLAG_TIMINGS) != 0;
    ptrdiff_t step = iio_buffer_step(c->rx_buffer);
    uint64_t sweep_started = monotonic_ns();
    for (group = 0; group < c->cfg.num_retunes; group += FASTLOCK_SLOTS) {
        uint32_t count = c->cfg.num_retunes - group;
        if (count > FASTLOCK_SLOTS) count = FASTLOCK_SLOTS;
        for (slot = 0; slot < count; ++slot) {
            index = group + slot;
            if (load_profile(c->rx_lo, c->rx_profiles[index], slot, timings, timings_enabled, SIDE_RX, index) ||
                load_profile(c->tx_lo, c->tx_profiles[index], slot, timings, timings_enabled, SIDE_TX, index)) {
                snprintf(error, size, "failed loading fastlock profile %u", index); return -1;
            }
        }
        for (slot = 0; slot < count; ++slot) {
            index = group + slot;
            if (recall_profile(c->rx_lo, slot, timings, timings_enabled, SIDE_RX, index) ||
                recall_profile(c->tx_lo, slot, timings, timings_enabled, SIDE_TX, index)) {
                snprintf(error, size, "failed recalling fastlock profile %u", index); return -1;
            }
            if (sleep_us(c->cfg.retune_delay_us) < 0) { snprintf(error, size, "retune settling sleep failed"); return -1; }
            for (average = 0; average < c->cfg.capture_averages; ++average) {
                char *ip[2], *qp[2];
                uint64_t started = monotonic_ns();
                ssize_t refill = iio_buffer_refill(c->rx_buffer);
                int status = refill < 0 ? (int)refill : 0;
                if (timing_append(timings, timings_enabled, TIMING_BUFFER_REFILL, SIDE_RX,
                                  (uint8_t)slot, index, average, status, started) < 0) {
                    snprintf(error, size, "out of memory recording timings"); return -1;
                }
                if (refill < 0) { snprintf(error, size, "RX buffer refill failed at frequency %u", index); return -1; }
                for (port = 0; port < 2; ++port) {
                    ip[port] = iio_buffer_first(c->rx_buffer, c->rx_i[port]);
                    qp[port] = iio_buffer_first(c->rx_buffer, c->rx_q[port]);
                }
                for (sample = 0; sample < c->cfg.buffer_size; ++sample) {
                    size_t offset = ((((size_t)index * c->cfg.capture_averages + average) * c->cfg.buffer_size + sample) * 4u);
                    uint32_t loop = c->cfg.rx_loopback_port, signal = c->cfg.rx_signal_port;
                    raw[offset] = *(int16_t *)ip[loop]; raw[offset + 1] = *(int16_t *)qp[loop];
                    raw[offset + 2] = *(int16_t *)ip[signal]; raw[offset + 3] = *(int16_t *)qp[signal];
                    for (port = 0; port < 2; ++port) { ip[port] += step; qp[port] += step; }
                }
            }
        }
    }
    *acquisition_ns = monotonic_ns() - sweep_started; return 0;
}
static int handle_configure(struct controller *c, const uint8_t *payload, size_t length) {
    struct timing_vector timings = {0};
    uint8_t *response;
    uint32_t count;
    size_t response_len;
    char error[256];
    if (configure_controller(c, payload, length, &timings, error, sizeof(error)) < 0) {
        timing_clear(&timings); return send_error(MSG_CONFIGURE, error);
    }
    count = (uint32_t)timings.count;
    response_len = sizeof(count) + timings.count * sizeof(*timings.items);
    response = malloc(response_len);
    if (!response) { timing_clear(&timings); return send_error(MSG_CONFIGURE, "out of memory building configure response"); }
    memcpy(response, &count, sizeof(count));
    if (timings.count) memcpy(response + sizeof(count), timings.items, timings.count * sizeof(*timings.items));
    int result = send_response(MSG_CONFIGURE, 0u, response, response_len);
    free(response); timing_clear(&timings); return result;
}
static int handle_sweep(struct controller *c) {
    struct timing_vector timings = {0};
    struct sweep_prefix prefix;
    int16_t *raw;
    uint64_t raw_bytes, response_len, acquisition_ns = 0;
    struct message_header header;
    char error[256];
    if (!c->configured) return send_error(MSG_SWEEP, "controller is not configured");
    raw_bytes = (uint64_t)c->cfg.num_retunes * c->cfg.capture_averages * c->cfg.buffer_size * 8u;
    raw = malloc((size_t)raw_bytes);
    if (!raw) return send_error(MSG_SWEEP, "out of memory allocating raw sweep");
    if (capture_sweep(c, raw, &timings, &acquisition_ns, error, sizeof(error)) < 0) {
        free(raw); timing_clear(&timings); return send_error(MSG_SWEEP, error);
    }
    prefix = (struct sweep_prefix) { c->cfg.num_retunes, c->cfg.capture_averages,
        c->cfg.buffer_size, 2u, (uint32_t)timings.count, acquisition_ns };
    response_len = sizeof(prefix) + timings.count * sizeof(*timings.items) + raw_bytes;
    memcpy(header.magic, MAGIC, 4);
    header.version = PROTOCOL_VERSION; header.type = MSG_SWEEP;
    header.status = 0u; header.payload_len = response_len;
    if (write_full(&header, sizeof(header)) < 0 ||
        write_full(&prefix, sizeof(prefix)) < 0 ||
        (timings.count && write_full(timings.items, timings.count * sizeof(*timings.items)) < 0) ||
        write_full(raw, (size_t)raw_bytes) < 0) {
        free(raw); timing_clear(&timings); return -1;
    }
    free(raw);
    timing_clear(&timings); return 0;
}
static int run_stdio(void) {
    struct controller controller = {0};
    struct message_header header;
    uint8_t *payload = NULL;
    bool running = true;
    while (running) {
        int read_status = read_full(&header, sizeof(header));
        if (read_status == 0) break;
        if (read_status < 0) goto error;
        if (memcmp(header.magic, MAGIC, 4) || header.version != PROTOCOL_VERSION) {
            send_error(header.type, "protocol magic or version mismatch"); goto error;
        }
        if (header.payload_len > MAX_CAPTURE_BYTES) { send_error(header.type, "command payload is too large"); goto error; }
        payload = NULL;
        if (header.payload_len) {
            payload = malloc((size_t)header.payload_len);
            if (!payload || read_full(payload, (size_t)header.payload_len) != 1) { free(payload); goto error; }
        }
        if (header.type == MSG_CONFIGURE) {
            if (handle_configure(&controller, payload, (size_t)header.payload_len) < 0) goto error;
        } else if (header.type == MSG_SWEEP) {
            if (header.payload_len || handle_sweep(&controller) < 0) goto error;
        } else if (header.type == MSG_PING) {
            uint32_t version = PROTOCOL_VERSION;
            if (send_response(MSG_PING, 0u, &version, sizeof(version)) < 0) goto error;
        } else if (header.type == MSG_SHUTDOWN) {
            if (send_response(MSG_SHUTDOWN, 0u, NULL, 0u) < 0) goto error;
            running = false;
        } else if (send_error(header.type, "unknown controller command") < 0) goto error;
        free(payload); payload = NULL;
    }
    controller_cleanup(&controller); return 0;
error:
    free(payload); controller_cleanup(&controller); return 1;
}
int main(int argc, char **argv) {
    int lock_fd, status;
    if (argc != 2 || strcmp(argv[1], "--stdio")) {
        fprintf(stderr, "usage: %s --stdio\n", argv[0]); return 2;
    }
    lock_fd = open("/var/lock/sfcw_controller.lock", O_CREAT | O_RDWR, 0644);
    if (lock_fd < 0 || flock(lock_fd, LOCK_EX | LOCK_NB) < 0) {
        fprintf(stderr, "another SFCW controller already owns the radio\n");
        if (lock_fd >= 0) close(lock_fd);
        return 3;
    }
    setvbuf(stdout, NULL, _IONBF, 0);
    status = run_stdio(); close(lock_fd); return status;
}
