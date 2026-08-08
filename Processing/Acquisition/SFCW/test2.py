import adi
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

sdr = adi.ad9361(uri="usb:")
sdr.sample_rate = int(20e6)
sdr.rx_lo = sdr.tx_lo = int(2.4e9)
sdr.rx_enabled_channels = [0, 1]
sdr.tx_enabled_channels = [0, 1]  # TX0 antenna, TX1 loopback
sdr.rx_buffer_size = 128
sdr.tx_cyclic_buffer = True
sdr.gain_control_mode_chan0 = sdr.gain_control_mode_chan1 = "manual"
sdr.rx_hardwaregain_chan0 = 20
sdr.rx_hardwaregain_chan1 = 50
sdr.tx_hardwaregain_chan0 = 0
sdr.tx_hardwaregain_chan1 = -25

n = np.arange(128)
tone_frequency = 7 * sdr.sample_rate / len(n)  # 1.09375 MHz; 7 cycles/buffer
tx_ant = (
    2**14 * 0.5 * np.exp(2j * np.pi * tone_frequency * n / sdr.sample_rate)
).astype(np.complex64)
tx_loopback = tx_ant.copy()
tone_mixer = np.exp(-2j * np.pi * tone_frequency * n / sdr.sample_rate)
rf_frequencies = np.arange(2.4e9, 2.5e9 + 1, 10e6, dtype=int)
reference_frequency = rf_frequencies[0]
calibration_phases = {}
delay_phase_slope = None

sdr.tx([tx_ant, tx_loopback])

fig, axes = plt.subplots(5, 1, sharex=True)
axes[0].plot(np.real(tx_ant))
axes[0].set_title("TX0 antenna")
axes[1].plot(np.real(tx_loopback))
axes[1].set_title("TX1 loopback (-25 dB, same programmed phase)")
rx_ant_raw_line, = axes[2].plot(n, np.zeros_like(n))
axes[2].set_title("RX0 antenna (uncorrected)")
rx_ant_corrected_line, = axes[3].plot(n, np.zeros_like(n))
axes[3].set_title("RX0 antenna (collecting wavelength calibration)")
rx_loopback_line, = axes[4].plot(n, np.zeros_like(n))
axes[4].set_title("RX1 loopback")

for ax in axes:
    ax.set_ylabel("I amplitude")
axes[4].set_xlabel("Sample")
plt.tight_layout()


def update(frame):
    global delay_phase_slope

    rf_frequency = rf_frequencies[frame % len(rf_frequencies)]
    sdr.rx_lo = sdr.tx_lo = int(rf_frequency)
    sdr.rx()  # Discard the first buffer after retuning.
    rx_ant, rx_loopback = sdr.rx()

    # First remove the common phase measured by the loopback channel.
    loopback_phasor = np.mean(rx_loopback * tone_mixer)
    rx_ant_corrected = rx_ant * np.exp(-1j * np.angle(loopback_phasor))
    antenna_phasor = np.mean(rx_ant_corrected * tone_mixer)

    # Use the first complete sweep to estimate and remove linear delay phase.
    if delay_phase_slope is None:
        calibration_phases[int(rf_frequency)] = np.angle(antenna_phasor)
        if len(calibration_phases) == len(rf_frequencies):
            measured_phases = np.unwrap([
                calibration_phases[int(f)] for f in rf_frequencies
            ])
            delay_phase_slope = np.polyfit(
                rf_frequencies - reference_frequency, measured_phases, 1
            )[0]

    wavelength_phase = (
        0.0 if delay_phase_slope is None
        else delay_phase_slope * (rf_frequency - reference_frequency)
    )
    rx_ant_corrected *= np.exp(-1j * wavelength_phase)
    corrected_phasor = np.mean(rx_ant_corrected * tone_mixer)

    rx_ant_raw_line.set_ydata(np.real(rx_ant))
    rx_ant_corrected_line.set_ydata(np.real(rx_ant_corrected))
    rx_loopback_line.set_ydata(np.real(rx_loopback))
    status = "calibrating" if delay_phase_slope is None else "wavelength-corrected"
    axes[3].set_title(
        f"RX0 loopback- and {status} - {rf_frequency / 1e9:.3f} GHz, "
        f"phase {np.angle(corrected_phasor, deg=True):.1f} degrees"
    )
    for ax in axes[2:]:
        ax.relim()
        ax.autoscale_view(scalex=False, scaley=True)
    return rx_ant_raw_line, rx_ant_corrected_line, rx_loopback_line


animation = FuncAnimation(
    fig, update, interval=100, blit=False, cache_frame_data=False
)

try:
    plt.show()
finally:
    sdr.tx_destroy_buffer()
    sdr.rx_destroy_buffer()
