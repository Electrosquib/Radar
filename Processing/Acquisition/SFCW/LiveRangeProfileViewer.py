from SFCW import SFCWRadar
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

CALIBRATE = False
SWEEP_AVERAGES = 4
HISTORY_LENGTH = 10
SLOW_TIME_HISTORY = 100

radar = SFCWRadar(
    verbose=True,
    Fmin=2500e6,
    Fmax=2800e6,
    Fs=20e6
)

input("Press Enter to start the live range profile viewer...")

# radar.auto_optimize_gains()
# if CALIBRATE:
#     radar.calibrate(num_samples=20)

fig, (ax, ax_slow) = plt.subplots(
    2,
    1,
    figsize=(11, 9),
    height_ratios=[1, 1]
)

history_lines = [
    ax.plot([], [], color="red", alpha=max(0.1, 0.7 - 0.06 * i), zorder=1)[0]
    for i in range(HISTORY_LENGTH)
]

line, = ax.plot([], [], color="blue", zorder=2)

profile_history = []
complex_rp_hist = []
slow_time_history = []
scan_count = 0

ax.set_title("Live Averaged SFCW Range Profile")
ax.set_xlabel("Range / Fast Time (m)")
ax.set_ylabel("Magnitude (dB)")
ax.set_xlim(0, 10)
ax.grid(True)

slow_image = ax_slow.imshow(
    np.zeros((1, 1)),
    aspect="auto",
    origin="lower",
    interpolation="nearest"
)

ax_slow.set_title("Range–Slow-Time")
ax_slow.set_xlabel("Range / Fast Time (m)")
ax_slow.set_ylabel("Slow Time (Scan)")
ax_slow.set_xlim(0, 10)

colorbar = fig.colorbar(slow_image, ax=ax_slow)
colorbar.set_label("Magnitude (dB)")

plt.tight_layout()

def update(_):
    global scan_count

    radar.sweep_average(SWEEP_AVERAGES)
    range_axis, rp = radar.get_range_profile(cal=False, plot=False)

    scan_count += 1
    complex_rp_hist.append(rp.copy())

    profiles = np.stack(complex_rp_hist)
    mean_rp = profiles.mean(axis=0)

    if len(complex_rp_hist) > 1:
        stability_error = np.sqrt(
            np.mean(np.abs(profiles - mean_rp) ** 2) /
            (np.mean(np.abs(mean_rp) ** 2) + 1e-12)
        )

        stability_db = -20 * np.log10(stability_error + 1e-12)

        print(
            f"Stability ({len(complex_rp_hist)} scans): "
            f"{stability_db:.2f} dB"
        )

    rp_db = 20 * np.log10(np.abs(rp) + 1e-12)

    displayed_profiles = [rp_db, *profile_history]

    for history_line, history_profile in zip(
        history_lines,
        reversed(profile_history)
    ):
        history_line.set_data(range_axis, history_profile)

    for history_line in history_lines[len(profile_history):]:
        history_line.set_data([], [])

    line.set_data(range_axis, rp_db)

    profile_history.append(rp_db.copy())

    if len(profile_history) > HISTORY_LENGTH:
        profile_history.pop(0)

    display_min = min(np.min(p) for p in displayed_profiles)
    display_max = max(np.max(p) for p in displayed_profiles)

    ax.set_ylim(display_min - 1, display_max + 1)

    slow_time_history.append(rp_db.copy())

    if len(slow_time_history) > SLOW_TIME_HISTORY:
        slow_time_history.pop(0)

    slow_data = np.stack(slow_time_history)

    first_scan = scan_count - len(slow_time_history) + 1
    last_scan = scan_count

    slow_image.set_data(slow_data)

    slow_image.set_extent([
        range_axis[0],
        range_axis[-1],
        first_scan - 0.5,
        last_scan + 0.5
    ])

    low = np.percentile(slow_data, 5)
    high = np.percentile(slow_data, 99)

    if high <= low:
        high = low + 1

    slow_image.set_clim(low, high)

    ax_slow.set_ylim(
        first_scan - 0.5,
        last_scan + 0.5
    )

    return line, *history_lines, slow_image

animation = FuncAnimation(
    fig,
    update,
    interval=100,
    blit=False,
    cache_frame_data=False
)

try:
    plt.show()
finally:
    radar.sdr.tx_destroy_buffer()
    radar.sdr.rx_destroy_buffer()