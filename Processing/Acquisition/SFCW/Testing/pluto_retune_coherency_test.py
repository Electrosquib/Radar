import adi
import numpy as np
import time
import matplotlib.pyplot as plt

DEVICE_STRING = "usb:"

fs = 1_000_000
fc = 915_000_000
tone_freq = 100_000
rx_buf_size = 16384
tx_gain = -30
rx1_gain = 10
rx2_gain = 40
num_captures = 300

sdr = adi.ad9361(uri=DEVICE_STRING)

sdr.sample_rate = fs
sdr.rx_rf_bandwidth = fs
sdr.tx_rf_bandwidth = fs
sdr.rx_lo = fc
sdr.tx_lo = fc
sdr.rx_buffer_size = rx_buf_size

sdr.rx_enabled_channels = [0, 1]
sdr.tx_enabled_channels = [0]

sdr.gain_control_mode_chan0 = "manual"
sdr.gain_control_mode_chan1 = "manual"
sdr.rx_hardwaregain_chan0 = rx1_gain
sdr.rx_hardwaregain_chan1 = rx2_gain
sdr.tx_hardwaregain_chan0 = tx_gain

sdr.tx_cyclic_buffer = True

Ntx = 2 ** 14
t_tx = np.arange(Ntx) / fs
tx = 0.5 * np.exp(2j * np.pi * tone_freq * t_tx)
tx = (tx * 2 ** 14).astype(np.complex64)

sdr.tx(tx)
time.sleep(0.5)

N = rx_buf_size
t = np.arange(N) / fs
bb_lo = np.exp(-2j * np.pi * tone_freq * t)

ref_vals = []
target_vals = []
corrected_vals = []

for i in range(num_captures):
    rx = sdr.rx()

    rx1 = rx[0]
    rx2 = rx[1]

    ref = np.mean(rx1 * bb_lo)
    target = np.mean(rx2 * bb_lo)

    corrected = target / ref

    ref_vals.append(ref)
    target_vals.append(target)
    corrected_vals.append(corrected)

    time.sleep(0.02)

sdr.tx_destroy_buffer()

ref_vals = np.array(ref_vals)
target_vals = np.array(target_vals)
corrected_vals = np.array(corrected_vals)

ref_phase = np.unwrap(np.angle(ref_vals))
target_phase = np.unwrap(np.angle(target_vals))
corrected_phase = np.unwrap(np.angle(corrected_vals))

ref_phase_error = ref_phase - np.mean(ref_phase)
target_phase_error = target_phase - np.mean(target_phase)
corrected_phase_error = corrected_phase - np.mean(corrected_phase)

ref_amp_db = 20 * np.log10(np.abs(ref_vals) / np.max(np.abs(ref_vals)) + 1e-12)
target_amp_db = 20 * np.log10(np.abs(target_vals) / np.max(np.abs(target_vals)) + 1e-12)
corrected_amp_db = 20 * np.log10(np.abs(corrected_vals) / np.max(np.abs(corrected_vals)) + 1e-12)

print("RX1 reference phase std deg:", np.std(ref_phase_error) * 180 / np.pi)
print("RX2 target phase std deg:", np.std(target_phase_error) * 180 / np.pi)
print("Corrected RX2/RX1 phase std deg:", np.std(corrected_phase_error) * 180 / np.pi)

print("RX1 reference amplitude std dB:", np.std(ref_amp_db))
print("RX2 target amplitude std dB:", np.std(target_amp_db))
print("Corrected amplitude std dB:", np.std(corrected_amp_db))

plt.figure()
plt.plot(ref_phase_error * 180 / np.pi, label="RX1 reference")
plt.plot(target_phase_error * 180 / np.pi, label="RX2 antenna")
plt.plot(corrected_phase_error * 180 / np.pi, label="RX2 / RX1 corrected")
plt.xlabel("Capture index")
plt.ylabel("Phase error deg")
plt.grid(True)
plt.legend()
plt.show()

plt.figure()
plt.plot(ref_amp_db, label="RX1 reference")
plt.plot(target_amp_db, label="RX2 antenna")
plt.plot(corrected_amp_db, label="RX2 / RX1 corrected")
plt.xlabel("Capture index")
plt.ylabel("Relative amplitude dB")
plt.grid(True)
plt.legend()
plt.show()