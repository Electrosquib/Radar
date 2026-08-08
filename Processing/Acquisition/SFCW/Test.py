import numpy as np
import adi
import matplotlib.pyplot as plt

sdr = adi.ad9361(uri="usb:")
sdr.sample_rate = int(20e6)
sdr.rx_lo = sdr.tx_lo = int(2.4e9)
sdr.rx_enabled_channels = sdr.tx_enabled_channels = [0, 1]
sdr.rx_buffer_size = 128
sdr.tx_cyclic_buffer = True
sdr.gain_control_mode_chan0 = sdr.gain_control_mode_chan1 = "manual"
sdr.rx_hardwaregain_chan0 = sdr.rx_hardwaregain_chan1 = 50
sdr.tx_hardwaregain_chan0 = sdr.tx_hardwaregain_chan1 = 0

n = np.arange(sdr.rx_buffer_size)
tx_ant = (2**14 * 0.5 * np.exp(2j * np.pi * 1e6 * n / sdr.sample_rate)).astype(np.complex64)

zero_rx = None
best_phase = None
best_rx = None
lowest_amplitude = np.inf

for phase_deg in range(360):
    tx_loopback = tx_ant * np.exp(1j * np.deg2rad(phase_deg))
    sdr.tx([tx_ant, tx_loopback])  # TX0 stays fixed; only TX1 phase changes.
    rx_ant = sdr.rx()[0]           # Evaluate only RX0 (antenna).
    sdr.tx_destroy_buffer()

    average_amplitude = np.mean(np.abs(rx_ant))
    if phase_deg == 0:
        zero_rx = rx_ant.copy()
    if average_amplitude < lowest_amplitude:
        lowest_amplitude = average_amplitude
        best_phase = phase_deg
        best_rx = rx_ant.copy()

print(f"Lowest RX0 average amplitude: {lowest_amplitude:.2f} at {best_phase} degrees")
plt.plot(20 * np.log10(np.abs(zero_rx) + 1e-12), label="0 degrees")
plt.plot(20 * np.log10(np.abs(best_rx) + 1e-12), label=f"Minimum: {best_phase} degrees")
plt.title("RX0 antenna: fixed TX0 vs phase-adjusted TX1 loopback")
plt.xlabel("Sample")
plt.ylabel("Magnitude (dB)")
plt.legend()
plt.show()
