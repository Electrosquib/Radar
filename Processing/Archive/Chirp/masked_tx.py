# import numpy as np
# from scipy.io import wavfile
# import matplotlib.pyplot as plt
# from scipy.signal import butter, filtfilt
from continuous_chirp import continuous_chirp
import signal, sys, time

# /opt/homebrew/Cellar/gnuradio/3.10.12.0_10/libexec/venv/bin/python Chirp/masked_tx.py 


# delta_r = c/2B
# fm_mod_sensitivity = 2 * pi * dev / (fs)

# subchirp_start = center_freq - fs/2
# subchirp_end = subchirp_start + .8fs
# pilot_freq = .9fs/2

fs = int(20e6)
chirp_start = int(5.0e9) # Chirp start frequency (Hz)
chirp_end = int(5.1e9) # Chirp end frequency (Hz, approximate as this depends on the chirp bandwidth)
chirp_overlap = 1
num_subchirps = int((chirp_end - chirp_start) // (chirp_overlap * fs))
bb_chirp_period = 50e-6
pilot_amplitude = 200e-3
rx_gain = .60
tx_gain = 1.0

print("[+] Number of subchirps:", num_subchirps)
print("[+] Approximate total scan file size:", int(num_subchirps * 12e3))
if chirp_start > chirp_end:
    print("[-] chirp_start must be less than chirp_end")
    exit()

center_freq = chirp_start + fs//2
tx = continuous_chirp(tx_gain=tx_gain, rx_gain=rx_gain, bb_chirp_period=50e-6, sdr_fs=fs)


def sig_handler(sig=None, frame=None):
    tx.stop()
    tx.wait()
    sys.exit(0)

signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

tx.start()
tx.flowgraph_started.set()

sweep_delay = 50e-3
chirp_period = 100e-3

try:
    for i in range(num_subchirps):
        print(f"Start: {center_freq - fs//2} | Center: {center_freq} | End: {center_freq - fs//2 + int(chirp_overlap  * fs)}")
        center_freq = center_freq - fs//2 + int(chirp_overlap  * fs) + fs //2
        tx.set_mask(1)
        time.sleep(chirp_period)
        tx.set_mask(0)
        t = time.monotonic()
        tx.set_center_freq(center_freq = center_freq)
        print(f"LO Change Time: {(t - time.monotonic())*.001}ms")
        time.sleep(sweep_delay)

except KeyboardInterrupt:
    pass

print("Done!")
tx.stop()