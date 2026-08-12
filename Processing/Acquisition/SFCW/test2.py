"""Single-frequency, two-transmitter self-interference cancellation test."""

import adi
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


# -----------------------------------------------------------------------------
# 1. Settings
# TX0 sends the wanted tone. TX1 sends an adjustable cancellation tone.
# RX0 measures the result. RX1 and LO-loopback correction are not used.
# -----------------------------------------------------------------------------

SDR_URI = "usb:"
LO_FREQUENCY = int(2.4e9)
SAMPLE_RATE = int(20e6)
BUFFER_SIZE = 2048
TONE_BIN = 7  # Integer bin keeps the cyclic waveform continuous.

TX_AMPLITUDE = 2**14 * 0.5
TX0_GAIN_DB = 0
TX1_GAIN_DB = 0
RX_GAIN_DB = 31

# Automatic SIC search settings.
SETTLE_BUFFERS = 2
MEASUREMENT_BUFFERS = 5
COARSE_PHASE_STEP_DEG = 10
FINE_PHASE_SPAN_DEG = 10
FINE_PHASE_STEP_DEG = 1
AMPLITUDE_STEPS = 51  # Searches ratios from 0.00 through 1.00.

PLOT_INTERVAL_MS = 100
ADC_CLIP_LEVEL = 0.90 * 2**11


# -----------------------------------------------------------------------------
# 2. Build the fixed-frequency tone
# The actual RF tone is the LO frequency plus this baseband tone frequency.
# -----------------------------------------------------------------------------

sample_numbers = np.arange(BUFFER_SIZE)
tone_frequency = TONE_BIN * SAMPLE_RATE / BUFFER_SIZE
transmit_frequency = LO_FREQUENCY + tone_frequency

tone_phase = 2 * np.pi * tone_frequency * sample_numbers / SAMPLE_RATE
unit_tone = np.exp(1j * tone_phase).astype(np.complex64)
tx_signal = (TX_AMPLITUDE * unit_tone).astype(np.complex64)

# Multiplying RX by this signal moves the known tone down to DC.
tone_demodulator = np.conj(unit_tone)


# -----------------------------------------------------------------------------
# 3. SDR setup
# TX1 is a cancellation output, not an LO loopback measurement channel.
# -----------------------------------------------------------------------------

def configure_sdr():
    sdr = adi.ad9361(uri=SDR_URI)
    sdr.sample_rate = SAMPLE_RATE
    sdr.rx_lo = LO_FREQUENCY
    sdr.tx_lo = LO_FREQUENCY
    sdr.rx_enabled_channels = [0]
    sdr.tx_enabled_channels = [0, 1]
    sdr.rx_buffer_size = BUFFER_SIZE
    sdr.tx_cyclic_buffer = True

    sdr.gain_control_mode_chan0 = "manual"
    sdr.rx_hardwaregain_chan0 = RX_GAIN_DB
    sdr.tx_hardwaregain_chan0 = TX0_GAIN_DB
    sdr.tx_hardwaregain_chan1 = TX1_GAIN_DB
    return sdr


# -----------------------------------------------------------------------------
# 4. SIC signal and measurement helpers
# Phase is explicitly converted from degrees to radians.
# The search minimizes power in the received tone, not mean(rx_signal).
# -----------------------------------------------------------------------------

def make_cancellation_signal(amplitude_ratio, phase_deg):
    phase_rad = np.deg2rad(phase_deg)
    cancellation_phasor = amplitude_ratio * np.exp(1j * phase_rad)
    return (TX_AMPLITUDE * cancellation_phasor * unit_tone).astype(np.complex64)


def start_cyclic_tx(sdr, cancellation_signal, tx_is_running):
    if tx_is_running:
        sdr.tx_destroy_buffer()
    sdr.tx([tx_signal, cancellation_signal])


def received_tone_power(rx_signal):
    """Return power in the one transmitted tone as a linear value."""
    tone_phasor = np.mean(rx_signal * tone_demodulator)
    return float(np.abs(tone_phasor) ** 2)


def measure_tone(sdr):
    # Ignore initial buffers after changing the cyclic TX waveform.
    for _ in range(SETTLE_BUFFERS):
        sdr.rx()

    rx_buffers = [sdr.rx() for _ in range(MEASUREMENT_BUFFERS)]
    powers = [received_tone_power(rx_signal) for rx_signal in rx_buffers]

    # Return the last buffer as a representative waveform for plotting.
    return float(np.mean(powers)), rx_buffers[-1]


def test_candidate(sdr, amplitude_ratio, phase_deg):
    cancellation_signal = make_cancellation_signal(amplitude_ratio, phase_deg)
    start_cyclic_tx(sdr, cancellation_signal, tx_is_running=True)
    power, _rx_signal = measure_tone(sdr)
    return power


# -----------------------------------------------------------------------------
# 5. Automatic cancellation search
# Run this with no target present. The selected settings are then frozen so the
# live measurement does not learn and cancel a stationary target reflection.
# -----------------------------------------------------------------------------

def calibrate_sic(sdr):
    zero_cancellation = np.zeros(BUFFER_SIZE, dtype=np.complex64)
    start_cyclic_tx(sdr, zero_cancellation, tx_is_running=False)
    baseline_power, baseline_signal = measure_tone(sdr)

    # First find the approximate cancellation phase at half amplitude.
    coarse_phases = np.arange(0, 360, COARSE_PHASE_STEP_DEG)
    coarse_powers = [test_candidate(sdr, 0.5, phase) for phase in coarse_phases]
    best_phase = float(coarse_phases[np.argmin(coarse_powers)])

    # At that phase, find the cancellation amplitude.
    amplitude_ratios = np.linspace(0.0, 1.0, AMPLITUDE_STEPS)
    amplitude_powers = [
        test_candidate(sdr, ratio, best_phase) for ratio in amplitude_ratios
    ]
    best_ratio = float(amplitude_ratios[np.argmin(amplitude_powers)])

    # Refine phase around the best coarse result using the selected amplitude.
    fine_phases = np.arange(
        best_phase - FINE_PHASE_SPAN_DEG,
        best_phase + FINE_PHASE_SPAN_DEG + FINE_PHASE_STEP_DEG,
        FINE_PHASE_STEP_DEG,
    )
    fine_powers = [test_candidate(sdr, best_ratio, phase) for phase in fine_phases]
    best_phase = float(fine_phases[np.argmin(fine_powers)] % 360)

    # Refine amplitude one more time at the improved phase.
    amplitude_powers = [
        test_candidate(sdr, ratio, best_phase) for ratio in amplitude_ratios
    ]
    best_index = int(np.argmin(amplitude_powers))
    best_ratio = float(amplitude_ratios[best_index])
    cancelled_power = float(amplitude_powers[best_index])

    # Leave TX running with the final, frozen cancellation waveform.
    final_cancellation = make_cancellation_signal(best_ratio, best_phase)
    start_cyclic_tx(sdr, final_cancellation, tx_is_running=True)
    for _ in range(SETTLE_BUFFERS):
        sdr.rx()

    cancellation_db = 10 * np.log10(
        baseline_power / max(cancelled_power, np.finfo(float).tiny)
    )
    return (
        final_cancellation,
        baseline_signal,
        best_ratio,
        best_phase,
        cancellation_db,
    )


# -----------------------------------------------------------------------------
# 6. Live plots
# Plot the two programmed outputs plus RX before and after analog SIC.
# -----------------------------------------------------------------------------

def run_live_plot(
    sdr,
    cancellation_signal,
    baseline_signal,
    ratio,
    phase_deg,
    calibration_db,
):
    figure, axes = plt.subplots(4, 1, sharex=True, figsize=(10, 9))
    tx0_axis, tx1_axis, before_axis, after_axis = axes

    tx0_axis.plot(sample_numbers, np.real(tx_signal))
    tx0_axis.set_title(
        f"TX0 signal (single freq): {transmit_frequency / 1e9:.6f} GHz"
    )

    tx1_axis.plot(sample_numbers, np.real(cancellation_signal))
    tx1_axis.set_title(
        f"TX1 SIC: amplitude ratio {ratio:.3f}, phase {phase_deg:.1f} degrees"
    )

    # This trace was captured during calibration with TX1 set to zero.
    baseline_i = np.real(baseline_signal)
    before_axis.plot(sample_numbers, baseline_i)
    before_axis.set_title("RX0 before SIC: cancellation disabled")

    # This trace updates continuously with the selected SIC signal enabled.
    (after_line,) = after_axis.plot(sample_numbers, np.zeros(BUFFER_SIZE))
    after_axis.set_xlabel("Sample")

    # Use the same fixed scale before and after so cancellation is easy to see.
    rx_limit = max(float(np.max(np.abs(baseline_i))) * 1.1, 1.0)
    before_axis.set_ylim(-rx_limit, rx_limit)
    after_axis.set_ylim(-rx_limit, rx_limit)

    for axis in axes:
        axis.set_ylabel("I amplitude")

    def update_plot(_frame):
        rx_signal = sdr.rx()
        after_line.set_ydata(np.real(rx_signal))

        live_power = received_tone_power(rx_signal)
        live_level_db = 10 * np.log10(max(live_power, np.finfo(float).tiny))
        peak_component = max(
            np.max(np.abs(np.real(rx_signal))),
            np.max(np.abs(np.imag(rx_signal))),
        )
        clip_warning = (
            " - WARNING: RX NEAR CLIPPING"
            if peak_component >= ADC_CLIP_LEVEL
            else ""
        )
        after_axis.set_title(
            f"RX0 after SIC: tone power {live_level_db:.1f} dB; "
            f"calibration improvement {calibration_db:.1f} dB{clip_warning}"
        )
        return (after_line,)

    figure.tight_layout()
    animation = FuncAnimation(
        figure,
        update_plot,
        interval=PLOT_INTERVAL_MS,
        blit=False,
        cache_frame_data=False,
    )
    plt.show()
    return animation


# -----------------------------------------------------------------------------
# 7. Run and clean up
# Keep hardware actions inside main so importing this file does not transmit.
# -----------------------------------------------------------------------------

def main():
    sdr = configure_sdr()
    try:
        print("Calibrating SIC. Keep the measurement area free of targets...")
        (
            cancellation_signal,
            baseline_signal,
            ratio,
            phase_deg,
            cancellation_db,
        ) = calibrate_sic(sdr)
        print(
            f"SIC fixed at amplitude ratio {ratio:.3f}, phase {phase_deg:.1f} deg; "
            f"measured improvement {cancellation_db:.1f} dB"
        )
        run_live_plot(
            sdr,
            cancellation_signal,
            baseline_signal,
            ratio,
            phase_deg,
            cancellation_db,
        )
    finally:
        sdr.tx_destroy_buffer()
        sdr.rx_destroy_buffer()


if __name__ == "__main__":
    main()
