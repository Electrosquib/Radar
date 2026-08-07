from SFCW import SFCWRadar

CALIBRATE = False
SWEEP_AVERAGES = 4
HISTORY_LENGTH = 10



# AI-generated animation code:
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

radar = SFCWRadar(verbose=False, Fmin=3000e6, Fmax=4000e6, Fs=20e6)

input("Press Enter to start the live range profile viewer...")

# radar.auto_optimize_gains()
# if CALIBRATE:
#     radar.calibrate(num_samples=20)

fig, ax = plt.subplots(figsize=(11, 5))
history_lines = [
    ax.plot([], [], color="red", alpha=0.7 - 0.06 * i, zorder=1)[0]
    for i in range(HISTORY_LENGTH)
]
profile_history = []
line, = ax.plot([], [], color="blue", zorder=2)
y_min, y_max = np.inf, -np.inf

ax.set_title("Live Averaged SFCW Range Profile")
ax.set_xlabel("Range (m)")
ax.set_ylabel("Magnitude (dB)")
ax.set_xlim(0, 10)
ax.grid(True)

def update(_):
    global y_min, y_max
    radar.sweep_average(SWEEP_AVERAGES)
    # radar.sweep()
    range_axis, rp = radar.get_range_profile(cal=False, plot=False)
    # range_axis, rp = radar.get_range_profile(cal="/Users/levifarinas/Library/Mobile Documents/com~apple~CloudDocs/Projects/SAR Backprojection/calibration.npy")
    rp_db = 20 * np.log10(np.abs(rp) + 1e-12)
    for history_line, history_profile in zip(history_lines, reversed(profile_history)):
        history_line.set_data(range_axis, history_profile)
    for history_line in history_lines[len(profile_history):]:
        history_line.set_data([], [])
    line.set_data(range_axis, rp_db)
    profile_history.append(rp_db.copy())
    if len(profile_history) > HISTORY_LENGTH:
        profile_history.pop(0)
    y_min = min(y_min, np.min(rp_db))
    y_max = max(y_max, np.max(rp_db))
    ax.set_ylim(y_min - 1, y_max + 1)
    return line, *history_lines

animation = FuncAnimation(
    fig,
    update,
    interval=100,
    blit=True,
    cache_frame_data=False
)

try:
    plt.show()
finally:
    radar.sdr.tx_destroy_buffer()
    radar.sdr.rx_destroy_buffer()
