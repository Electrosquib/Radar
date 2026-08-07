import adi
import time
import numpy as np
import matplotlib.pyplot as plt

DEVICE_STRING = "usb:"

START_FREQ = int(1e9)
RADAR_BW = int(1000e6)
FREQ_STEP = int(10e6)

FS = int(1e6)
SDR_BW = int(12e6)
RX_BUF_SIZE = 128
BB_FREQ = int(100e3)

TX_GAIN = 0
RX_LOOPBACK_GAIN = 10
RX_GAIN = 40

BB_AMP = 0.5
SDR_SCALER = 2 ** 14
SETTLE_TIME = 0.05
CAPTURE_AVERAGES = 3
C = 3e8

CENTER_FREQS = np.arange(START_FREQ, START_FREQ + RADAR_BW, FREQ_STEP)
N_STEPS = len(CENTER_FREQS)
ACTUAL_BW = N_STEPS * FREQ_STEP

range_res = C / (2 * ACTUAL_BW)
range_max = C / (2 * FREQ_STEP)

print("Steps:", N_STEPS)
print("Actual BW MHz:", ACTUAL_BW / 1e6)
print("Range resolution m:", range_res)
print("Max unambiguous range m:", range_max)

sdr = adi.ad9361(uri=DEVICE_STRING)

sdr.rx_enabled_channels = [0, 1]
sdr.tx_enabled_channels = [0]

sdr.sample_rate = FS
sdr.rx_rf_bandwidth = SDR_BW
sdr.tx_rf_bandwidth = SDR_BW
sdr.rx_buffer_size = RX_BUF_SIZE

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

t_rx = np.arange(RX_BUF_SIZE) / FS
bb_lo = np.exp(-2j * np.pi * BB_FREQ * t_rx)

rx_vals = np.zeros(N_STEPS, dtype=np.complex64)
loop_vals = np.zeros(N_STEPS, dtype=np.complex64)
S = np.zeros(N_STEPS, dtype=np.complex64)

last_rx = None
last_loop = None

for i, fc in enumerate(CENTER_FREQS):
    fc = int(fc)

    try:
        sdr.tx_destroy_buffer()
    except Exception:
        pass

    sdr.tx_lo = fc
    sdr.rx_lo = fc
    time.sleep(SETTLE_TIME)

    sdr.tx(tx)
    time.sleep(SETTLE_TIME)

    loop_sum = 0
    rx_sum = 0

    for _ in range(CAPTURE_AVERAGES):
        samps = sdr.rx()

        loop_raw = samps[0] - np.mean(samps[0])
        rx_raw = samps[1] - np.mean(samps[1])

        loop_phasor = np.mean(loop_raw * bb_lo)
        rx_phasor = np.mean(rx_raw * bb_lo)

        loop_sum += loop_phasor
        rx_sum += rx_phasor

        last_loop = loop_raw
        last_rx = rx_raw

    loop_vals[i] = loop_sum / CAPTURE_AVERAGES
    rx_vals[i] = rx_sum / CAPTURE_AVERAGES
    S[i] = rx_vals[i] / (loop_vals[i] + 1e-12)

    print(f"{i + 1}/{N_STEPS} fc={fc / 1e9:.3f} GHz | loop={20*np.log10(abs(loop_vals[i])+1e-12):.1f} dB | rx={20*np.log10(abs(rx_vals[i])+1e-12):.1f} dB")

S_raw = S.copy()
S = S - np.mean(S)
window = np.hanning(N_STEPS)
rp = np.fft.ifft(S * window, n=N_STEPS)

rp_mag = np.abs(rp)
rp_db = 20 * np.log10(rp_mag / np.max(rp_mag) + 1e-12)
range_axis = np.arange(N_STEPS) * C / (2 * ACTUAL_BW)

plt.close("all")

fig, ax = plt.subplots(5, 1, figsize=(11, 12))

ax[0].plot(np.abs(last_loop), label="RX0 loopback")
ax[0].plot(np.abs(last_rx), label="RX1 target")
ax[0].set_title("Last capture raw magnitude")
ax[0].set_ylabel("ADC magnitude")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(CENTER_FREQS / 1e9, 20 * np.log10(np.abs(loop_vals) + 1e-12), label="Loopback")
ax[1].plot(CENTER_FREQS / 1e9, 20 * np.log10(np.abs(rx_vals) + 1e-12), label="RX")
ax[1].set_title("Extracted tone magnitude vs frequency")
ax[1].set_xlabel("Frequency GHz")
ax[1].set_ylabel("Magnitude dB")
ax[1].legend()
ax[1].grid(True)

ax[2].plot(CENTER_FREQS / 1e9, np.unwrap(np.angle(loop_vals)) * 180 / np.pi, label="Loopback")
ax[2].plot(CENTER_FREQS / 1e9, np.unwrap(np.angle(rx_vals)) * 180 / np.pi, label="RX")
ax[2].set_title("Raw phase vs frequency")
ax[2].set_xlabel("Frequency GHz")
ax[2].set_ylabel("Phase deg")
ax[2].legend()
ax[2].grid(True)

ax[3].plot(CENTER_FREQS / 1e9, np.abs(S_raw))
ax[3].set_title("Corrected magnitude |RX / Loopback|")
ax[3].set_xlabel("Frequency GHz")
ax[3].set_ylabel("Magnitude")
ax[3].grid(True)

ax[4].plot(range_axis, rp_db)
ax[4].set_title("Stepped-CW range profile")
ax[4].set_xlabel("Range m")
ax[4].set_ylabel("Magnitude dB")
ax[4].set_ylim(-60, 0)
ax[4].set_xlim(0, range_max)
ax[4].grid(True)

plt.tight_layout()
plt.show()

plt.figure(figsize=(11, 5))
plt.plot(range_axis, rp_db)
plt.title("Range Profile")
plt.xlabel("Range m")
plt.ylabel("Magnitude dB")
plt.ylim(-60, 0)
plt.xlim(0, range_max)
plt.grid(True)
plt.show()