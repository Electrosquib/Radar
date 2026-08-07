# Notes:
# Treat the Pluto SDR clones as AD9361 instead of AD9363 so you can expose the 2x2 MIMO
# Loopback: RX channel 0
# RX: RX channel 1
# TX: TX channel 0

import adi
import time
import numpy as np
import matplotlib.pyplot as plt

DEVICE_STRING = "usb:"
# DEVICE_STRING = "ip:192.168.2.1"

START_FREQ = 500e6
FREQ_STEP = 10e6
RADAR_BW = 2e9 - START_FREQ
FS = 1e6
SDR_BW = 1e6
RX_BUF_SIZE = 4096
RX_WAIT_TIME = .01
RX_GAIN = 70
RX_LOOPBACK_GAIN = 70
TX_GAIN = 0 # This is actually attenuation
BB_FREQ = 100e3
BB_AMP = 1
STEP_DELAY = .01
SDR_SCALER = 2**14
C = 3e8
RANGE_RES = C / (2 * RADAR_BW)

CENTER_FREQS = np.arange(START_FREQ, START_FREQ+RADAR_BW, FREQ_STEP)
N_STEPS = len(CENTER_FREQS)
FS = int(FS)
SDR_BW = int(SDR_BW)
BB_FREQ = int(BB_FREQ)
sdr = adi.ad9361(uri=DEVICE_STRING)
sdr.rx_enabled_channels = [0, 1]
sdr.tx_enabled_channels = [0]

sdr.sample_rate = FS
sdr.rx_rf_bandwidth = SDR_BW
sdr.rx_buffer_size = RX_BUF_SIZE
sdr.tx_rf_bandwidth = SDR_BW
sdr.tx_cyclic_buffer = False

sdr.gain_control_mode_chan0 = "manual"
sdr.gain_control_mode_chan1 = "manual"
sdr.rx_hardwaregain_chan0 = RX_LOOPBACK_GAIN
sdr.rx_hardwaregain_chan1 = RX_GAIN
sdr.tx_hardwaregain_chan0 = TX_GAIN

TX_N = int(RX_BUF_SIZE + RX_WAIT_TIME * FS)
t = np.arange(TX_N) / FS
cw_iq = SDR_SCALER * BB_AMP * np.exp(-2j * np.pi * BB_FREQ * t).astype(np.complex64)
cw_mix = cw_iq[:RX_BUF_SIZE]

S = np.zeros(CENTER_FREQS.shape, dtype=np.complex64)
count = 0
# for i, center_freq in enumerate(CENTER_FREQS):
center_freq = CENTER_FREQS[0]
center_freq = int(center_freq)
sdr.tx_lo = center_freq
sdr.rx_lo = center_freq
sdr.tx(cw_iq)
# time.sleep(RX_WAIT_TIME)
rx_samps = sdr.rx()
loopback = np.mean(rx_samps[0] * cw_mix) # Mix to extract BB tone, then average to collapse into single phasor
rx = np.mean(rx_samps[1] * cw_mix)
# S[i] = rx / loopback
time.sleep(STEP_DELAY)

rp = np.fft.ifft(S, n=N_STEPS)
rp_db = 20 * np.log10(np.abs(rp) / np.max(np.abs(rp)) + 1e-12)
range_axis = np.arange(N_STEPS) * C / (2 * FREQ_STEP * FREQ_STEP)

plt.close("all")

fig, ax = plt.subplots(4, 1, sharex=False, figsize=(10, 8))

ax[0].plot(np.abs(rx_samps[1]))
ax[0].set_title("RX")
ax[0].set_ylabel("Magnitude")
ax[0].grid(True)

ax[1].plot(np.abs(rx_samps[0]))
ax[1].set_title("Loopback")
ax[1].set_ylabel("Magnitude")
ax[1].grid(True)

# ax[2].plot(np.abs(S))
# ax[2].set_title("Corrected S")
# ax[2].set_ylabel("Magnitude")
# ax[2].grid(True)

# ax[3].plot(range_axis, rp_db)
# ax[3].set_title("Range Profile")
# ax[3].set_xlabel("Range m")
# ax[3].set_ylabel("Magnitude dB")
# ax[3].set_ylim(-60, 0)
# ax[3].grid(True)

plt.tight_layout()
plt.show()