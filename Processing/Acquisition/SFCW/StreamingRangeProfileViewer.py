if __name__ == "__main__" and globals().get("packet_source") is None:
    import argparse

    argparse.ArgumentParser(
        description="Display live SFCW range profiles and range-slow-time history.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Commands (from the repository root):
  python start_radar.py             Start USB capture and the browser viewer.
  python start_radar.py --rebuild   Compile and upload radar.c, then start USB capture.
  python start_radar.py --help      Show launcher options.

Running this viewer directly listens for UDP sweeps on 0.0.0.0:5000
(4.0-4.6 GHz, 2 MHz spacing); it does not start the radar sender.

Controls and status:
  Amplitude slider: adjust the trace and waterfall dB limits.
  Terminal output: sweep rate, stability, dropped packets, incomplete sweeps.
  Stop USB capture: Ctrl+C in the launcher terminal; closing the browser tab
  does not stop capture. Close the plot window to stop the standalone viewer.

USB setup: connect one PlutoSDR and close other programs using its serial console.
Rebuild/upload requires make and the ARM compiler configured by the Makefile."""
    ).parse_args()

from SFCW import StreamRangeProfiles
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RangeSlider
from collections import deque
from time import perf_counter
import matplotlib.pyplot as plt
import numpy as np

SWEEP_AVERAGES = 1
HISTORY_LENGTH = 10
SLOW_TIME_HISTORY = 100
RANGE_GATE_BINS = 2
WAITING_TITLE = ("Waiting for USB sweeps" if globals().get("packet_source") is not None
                 else "Waiting for UDP sweeps on port 5000")

radar = StreamRangeProfiles(
    host="0.0.0.0",
    port=5000,
    fmin=4.0e9,
    fmax=4.6e9,
    spacing=2e6,
    packet_source=globals().get("packet_source")
)
# Keep missing sweep data from blocking the GUI event loop.
radar.sock.settimeout(0.01)

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
arrival_times = deque(maxlen=20)

ax.set_title(WAITING_TITLE)
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

plt.tight_layout(rect=(0, 0.12, 1, 1))

amplitude_slider = RangeSlider(
    fig.add_axes([0.18, 0.045, 0.65, 0.03]),
    "Amplitude (dB)", -120, 80, valinit=(-60, 0), valstep=1, valfmt="%0.0f dB"
)

def set_amplitude(limits):
    low, high = limits
    if high <= low:
        high = low + 1
    ax.set_ylim(low, high)
    slow_image.set_clim(low, high)
    fig.canvas.draw_idle()

amplitude_slider.on_changed(set_amplitude)
set_amplitude(amplitude_slider.val)

def get_averaged_profile():
    profiles = []
    range_axis = None
    sweep_id = None

    for _ in range(SWEEP_AVERAGES):
        range_axis, rp, sweep_id = radar.get_range_profile()
        profiles.append(rp)

    return range_axis, np.mean(profiles, axis=0), sweep_id

def update(*_):
    global scan_count

    try:
        range_axis, rp, sweep_id = get_averaged_profile()
    except TimeoutError:
        if scan_count == 0:
            ax.set_title(WAITING_TITLE)
        return line, *history_lines, slow_image

    arrival_times.append(perf_counter())
    elapsed = arrival_times[-1] - arrival_times[0]
    hz = (len(arrival_times) - 1) / elapsed if elapsed > 0 else 0.0
    ax.set_title(f"Live Streamed SFCW Range Profile | {hz:.1f} Hz")
    status = f"Sweep {sweep_id} | {hz:.1f} Hz"

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

        status += f" | Stability ({len(complex_rp_hist)} scans): {stability_db:.2f} dB"

    print(
        f"{status} | Dropped packets: {radar.dropped_packets} | "
        f"Incomplete sweeps: {radar.incomplete_sweeps}"
    )

    rp_db = 20 * np.log10(np.abs(rp) + 1e-12)

    gate_bins = min(RANGE_GATE_BINS, len(rp_db))
    rp_db[:gate_bins] = np.nan

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

    ax_slow.set_ylim(
        first_scan - 0.5,
        last_scan + 0.5
    )

    return line, *history_lines, slow_image

animation = FuncAnimation(
    fig,
    update,
    interval=1,
    blit=False,
    cache_frame_data=False
)

try:
    plt.show()
finally:
    radar.close()
