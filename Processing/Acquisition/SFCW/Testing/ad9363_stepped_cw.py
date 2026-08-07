import adi
import time
import numpy as np
import matplotlib.pyplot as plt

DEVICE_STRING = "usb:"

FC = int(915e6)
FS = int(1e6)
SDR_BW = int(1e6)
RX_BUF_SIZE = 4096 * 4
RX_GAIN = 40
RX_LOOPBACK_GAIN = 10
TX_GAIN = -50
BB_FREQ = int(100e3)
BB_AMP = 0.5
SDR_SCALER = 2 ** 14
NUM_CAPTURES = 300

sdr = adi.ad9361(uri=DEVICE_STRING)
sdr.rx_enabled_channels = [0, 1]
sdr.tx_enabled_channels = [0]

sdr.sample_rate = FS
sdr.rx_rf_bandwidth = SDR_BW
sdr.tx_rf_bandwidth = SDR_BW
sdr.rx_buffer_size = RX_BUF_SIZE

sdr.tx_lo = FC
sdr.rx_lo = FC

sdr.gain_control_mode_chan0 = "manual"
sdr.gain_control_mode_chan1 = "manual"
sdr.rx_hardwaregain_chan0 = RX_LOOPBACK_GAIN
sdr.rx_hardwaregain_chan1 = RX_GAIN
sdr.tx_hardwaregain_chan0 = TX_GAIN

sdr.tx_cyclic_buffer = True

Ntx = 2 ** 14
t_tx = np.arange(Ntx) / FS
tx = SDR_SCALER * BB_AMP * np.exp(2j * np.pi * BB_FREQ * t_tx)
tx = tx.astype(np.complex64)

sdr.tx_destroy_buffer()
sdr.tx(tx)
time.sleep(0.5)

N = RX_BUF_SIZE
t = np.arange(N) / FS
bb_lo = np.exp(-2j * np.pi * BB_FREQ * t)

ref_vals = np.zeros(NUM_CAPTURES, dtype=np.complex64)
target_vals = np.zeros(NUM_CAPTURES, dtype=np.complex64)
corrected_vals = np.zeros(NUM_CAPTURES, dtype=np.complex64)

last_ref = None
last_target = None
last_corrected_samples = None

for i in range(NUM_CAPTURES):
    rx_samps = sdr.rx()

    ref_raw = rx_samps[0]
    target_raw = rx_samps[1]

    ref_raw = ref_raw - np.mean(ref_raw)
    target_raw = target_raw - np.mean(target_raw)

    ref = np.mean(ref_raw * bb_lo)
    target = np.mean(target_raw * bb_lo)

    corrected = target / (ref + 1e-12)

    ref_vals[i] = ref
    target_vals[i] = target
    corrected_vals[i] = corrected

    last_ref = ref_raw
    last_target = target_raw
    last_corrected_samples = target_raw / (ref_raw + 1e-12)

    time.sleep(0.02)

sdr.tx_destroy_buffer()

ref_phase = np.unwrap(np.angle(ref_vals))
target_phase = np.unwrap(np.angle(target_vals))
corrected_phase = np.unwrap(np.angle(corrected_vals))

ref_phase_error = ref_phase - np.mean(ref_phase)
target_phase_error = target_phase - np.mean(target_phase)
corrected_phase_error = corrected_phase - np.mean(corrected_phase)

ref_amp_db = 20 * np.log10(np.abs(ref_vals) / np.max(np.abs(ref_vals)) + 1e-12)
target_amp_db = 20 * np.log10(np.abs(target_vals) / np.max(np.abs(target_vals)) + 1e-12)
corrected_amp_db = 20 * np.log10(np.abs(corrected_vals) / np.max(np.abs(corrected_vals)) + 1e-12)

print("RX0 loopback phase std deg:", np.std(ref_phase_error) * 180 / np.pi)
print("RX1 target phase std deg:", np.std(target_phase_error) * 180 / np.pi)
print("Corrected RX1/RX0 phase std deg:", np.std(corrected_phase_error) * 180 / np.pi)

print("RX0 loopback amplitude std dB:", np.std(ref_amp_db))
print("RX1 target amplitude std dB:", np.std(target_amp_db))
print("Corrected amplitude std dB:", np.std(corrected_amp_db))

plt.close("all")

fig, ax = plt.subplots(3, 1, figsize=(10, 8))

ax[0].plot(np.abs(last_ref), label="RX0 loopback")
ax[0].plot(np.abs(last_target), label="RX1 target")
ax[0].set_title("Last capture magnitude")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(np.unwrap(np.angle(last_ref * bb_lo)) * 180 / np.pi, label="RX0 loopback")
ax[1].plot(np.unwrap(np.angle(last_target * bb_lo)) * 180 / np.pi, label="RX1 target")
ax[1].set_title("Last capture mixed phase")
ax[1].set_ylabel("Degrees")
ax[1].legend()
ax[1].grid(True)

ax[2].plot(ref_phase_error * 180 / np.pi, label="RX0 loopback")
ax[2].plot(target_phase_error * 180 / np.pi, label="RX1 target")
ax[2].plot(corrected_phase_error * 180 / np.pi, label="RX1 / RX0 corrected")
ax[2].set_title("Phase stability across captures")
ax[2].set_xlabel("Capture index")
ax[2].set_ylabel("Phase error deg")
ax[2].legend()
ax[2].grid(True)

plt.tight_layout()
plt.show()

plt.figure()
plt.plot(ref_amp_db, label="RX0 loopback")
plt.plot(target_amp_db, label="RX1 target")
plt.plot(corrected_amp_db, label="RX1 / RX0 corrected")
plt.xlabel("Capture index")
plt.ylabel("Relative amplitude dB")
plt.grid(True)
plt.legend()
plt.show()

X0 = np.fft.fftshift(np.fft.fft(last_ref * np.hanning(len(last_ref))))
X1 = np.fft.fftshift(np.fft.fft(last_target * np.hanning(len(last_target))))
f = np.fft.fftshift(np.fft.fftfreq(len(last_ref), 1 / FS))

plt.figure()
plt.plot(f / 1e3, 20 * np.log10(np.abs(X0) / np.max(np.abs(X0)) + 1e-12), label="RX0 loopback")
plt.plot(f / 1e3, 20 * np.log10(np.abs(X1) / np.max(np.abs(X1)) + 1e-12), label="RX1 target")
plt.axvline(BB_FREQ / 1e3, linestyle="--")
plt.axvline(-BB_FREQ / 1e3, linestyle="--")
plt.xlabel("Frequency kHz")
plt.ylabel("Magnitude dB")
plt.ylim(-80, 0)
plt.grid(True)
plt.legend()
plt.show()