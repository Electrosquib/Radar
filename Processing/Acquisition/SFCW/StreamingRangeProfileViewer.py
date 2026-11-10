<<<<<<< HEAD
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
=======
import argparse
from pathlib import Path
import shlex
import socket
import subprocess
import threading
import time
import uuid
from collections import deque


def ssh_options(args, batch=False):
    options = ["-o", "ConnectTimeout=5", "-o", "ServerAliveInterval=5",
               "-o", "ServerAliveCountMax=3"]
    if args.ssh_key.expanduser().is_file():
        options += ["-i", str(args.ssh_key.expanduser()), "-o", "IdentitiesOnly=yes"]
    if batch:
        options += ["-o", "BatchMode=yes"]
    return options


def configure_ssh_login(args):
    """Add a scoped SSH config entry so terminal reconnects use the same key."""
    address = args.pluto_ip
    if any(c.isspace() for c in address) or any(c in address for c in '*?![]'):
        raise ValueError("Pluto SSH address must be a single host, not a config pattern")
    key = args.ssh_key.expanduser().resolve()
    config = Path.home() / ".ssh/config"
    config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    original = config.read_text() if config.exists() else ""
    begin = f"# BEGIN streaming-range-profile-pluto {address}"
    end = f"# END streaming-range-profile-pluto {address}"
    block = (f"{begin}\nHost {address} pluto-radar\n"
             f"    HostName {address}\n    User root\n"
             f'    IdentityFile "{key}"\n    IdentitiesOnly yes\n{end}\n')
    remaining = original
    if begin in original:
        start = original.index(begin)
        finish = original.find(end, start)
        if finish == -1:
            raise ValueError("Incomplete Pluto SSH config block; repair ~/.ssh/config first")
        remaining = original[:start] + original[finish + len(end):].lstrip("\n")
    updated = block + "\n" + remaining
    if updated != original:
        if original:
            backup = config.with_name("config.before-pluto-login")
            if not backup.exists():
                backup.write_text(original)
                backup.chmod(0o600)
        config.write_text(updated)
        config.chmod(0o600)


def setup_ssh_key(args):
    """Generate a dedicated login key and install it using one password login."""
    key = args.ssh_key.expanduser()
    if not key.is_file():
        key.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(key),
                        "-C", "pluto-range-profile-viewer"], check=True)
    target = f"root@{args.pluto_ip}"
    probe = subprocess.run(["ssh", *ssh_options(args, batch=True), target, "true"],
                           capture_output=True, text=True, timeout=10)
    if probe.returncode == 0:
        configure_ssh_login(args)
        print(f"[+] Passwordless Pluto login ready: {key}", flush=True)
        return
    public_key = subprocess.run(["ssh-keygen", "-y", "-f", str(key)],
                                capture_output=True, text=True, check=True).stdout.strip()
    print("[+] Installing public key on Pluto. Enter its SSH password once (default: analog).",
          flush=True)
    command = (
        'umask 077; mkdir -p /root/.ssh && chmod 700 /root/.ssh && '
        'key=$(cat) && touch /root/.ssh/authorized_keys && '
        '(grep -qxF "$key" /root/.ssh/authorized_keys || '
        'printf "\\n%s\\n" "$key" >> /root/.ssh/authorized_keys) && '
        'chmod 600 /root/.ssh/authorized_keys && '
        'if grep -q "^mtd2 /mnt/jffs2 jffs2 rw" /proc/mounts; then '
        '/usr/sbin/device_persistent_keys; else '
        'echo "[!] Public key installed for this boot only: persistent flash is not mounted."; fi'
    )
    subprocess.run(["ssh", *ssh_options(args), target, command],
                   input=public_key + "\n", text=True, check=True)
    subprocess.run(["ssh", *ssh_options(args, batch=True), target, "true"], check=True)
    configure_ssh_login(args)
    print(f"[+] Passwordless Pluto login verified: {key}", flush=True)


'''+'''

def prepare_pluto(args):
    """Optionally build and upload; SCP uses legacy mode for Pluto's Dropbear."""
    if not (args.deploy or args.skip_compile or args.deploy_only):
        return
    binary = args.binary.expanduser().resolve()
    if not args.skip_compile:
        subprocess.run(["make", "-C", str(binary.parent), "build"], check=True)
    if not binary.is_file():
        raise ValueError(f"Built executable not found: {binary}")
    with binary.open("rb") as executable:
        header = executable.read(20)
    if (len(header) < 20 or header[:4] != b"\x7fELF" or
            header[4:6] != b"\x01\x01" or header[18:20] != b"\x28\x00"):
        raise ValueError(f"Expected a 32-bit ARM Linux ELF executable: {binary}")
    try:
        with socket.create_connection((args.pluto_ip, 22), timeout=5):
            pass
    except OSError as exc:
        raise RuntimeError(
            f"Cannot reach Pluto SSH at {args.pluto_ip}:22: {exc}. "
            "Check the USB network interface and Pluto config.txt; macOS needs "
            "usb_ethernet_mode = ncm. Eject the Pluto drive after changing it."
        ) from exc
    target = f"root@{args.pluto_ip}"
    setup_ssh_key(args)
    options = ssh_options(args, batch=True)
    staging = f"/root/.radar-upload-{uuid.uuid4().hex}"
    try:
        subprocess.run(["scp", "-O", *options, str(binary),
                        f"{target}:{staging}"], check=True)
        subprocess.run(["ssh", *options, target,
                        f"chmod 700 {staging} && mv -f {staging} /root/radar"], check=True)
    except (OSError, subprocess.SubprocessError):
        try:
            subprocess.run(["ssh", *options, target, f"rm -f {staging}"],
                           timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, subprocess.SubprocessError):
            pass
        raise
    print(f"[+] Uploaded {binary} to {target}:/root/radar", flush=True)
    print("[+] Any running radar process keeps its current build; restart it to use this upload.", flush=True)
    print(f"[+] Start streaming in another terminal: ssh {shlex.quote(target)} "
          "'/root/radar'", flush=True)
    print("[+] This build sends UDP to 192.168.2.10:5000; "
          "the Mac's Pluto interface must use that address.", flush=True)


def parse_args():
    parser = argparse.ArgumentParser(description="View streamed SFCW range profiles.")
    parser.add_argument("--deploy", action="store_true", help="Build and upload before viewing.")
    parser.add_argument("--skip-compile", action="store_true",
                        help="Upload the existing ARM executable without running make.")
    parser.add_argument("--deploy-only", action="store_true",
                        help="Upload and exit without opening the viewer; combine with --skip-compile on macOS.")
    parser.add_argument("--binary", type=Path,
                        default=Path(__file__).resolve().parents[2] / "Firmware/Apps/radar",
                        help="Path to the built ARM executable (default: Firmware/Apps/radar).")
    parser.add_argument("--setup-ssh-key", action="store_true",
                        help="Set up passwordless Pluto login; exit unless an upload is also requested.")
    parser.add_argument("--ssh-key", type=Path, default=Path.home() / ".ssh/pluto_radar_ed25519",
                        help="Dedicated Pluto login key (default: ~/.ssh/pluto_radar_ed25519).")
    parser.add_argument("--pluto-ip", default="192.168.2.1", help="Pluto SSH address.")
    parser.add_argument("--mode", choices=("plot", "receive-only", "process-only"), default="plot",
                        help="Compare continuous UDP reception, DSP, and plotting.")
    parser.add_argument("--duration", type=float, default=30,
                        help="Headless measurement duration in seconds (default: 30).")
    parser.add_argument("--plot-hz", type=float, default=15, help="Plot refresh rate (default: 15 Hz).")
    parsed = parser.parse_args()
    if parsed.duration <= 0 or not 10 <= parsed.plot_hz <= 20:
        parser.error("--duration must be positive and --plot-hz must be between 10 and 20")
    return parsed


if __name__ == "__main__":
    args = parse_args()
    try:
        if args.setup_ssh_key:
            setup_ssh_key(args)
            if not (args.deploy or args.skip_compile or args.deploy_only):
                raise SystemExit(0)
        prepare_pluto(args)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"[-] {exc}") from exc
    if args.deploy_only:
        raise SystemExit(0)

from SFCW import StreamRangeProfiles
>>>>>>> eabd28fe9e2d8d9a95793bc8cbc0aa712df77da0
import numpy as np

SWEEP_AVERAGES = 1
HISTORY_LENGTH = 10
SLOW_TIME_HISTORY = 100
RANGE_GATE_BINS = 2
<<<<<<< HEAD
WAITING_TITLE = ("Waiting for USB sweeps" if globals().get("packet_source") is not None
                 else "Waiting for UDP sweeps on port 5000")
=======
COLOR_MIN_DB = -100.0
COLOR_MAX_DB = 0.0
COLOR_MAX_SLIDER_UPPER_DB = 100.0
>>>>>>> eabd28fe9e2d8d9a95793bc8cbc0aa712df77da0

radar = StreamRangeProfiles(
    host="0.0.0.0",
    port=5000,
<<<<<<< HEAD
    fmin=4.0e9,
    fmax=4.6e9,
    spacing=2e6,
    packet_source=globals().get("packet_source")
=======
    fmin=2.5e9,
    fmax=2.8e9,
    spacing=2e6,
    verbose=False
>>>>>>> eabd28fe9e2d8d9a95793bc8cbc0aa712df77da0
)
# Keep missing sweep data from blocking the GUI event loop.
radar.sock.settimeout(0.01)

print(f"[+] SO_RCVBUF actual={radar.actual_receive_buffer_bytes} bytes | mode={args.mode}")


def run_measurement():
    samples = []
    deadline = time.perf_counter() + args.duration
    try:
        while time.perf_counter() < deadline:
            try:
                if args.mode == "receive-only":
                    radar.receive_sweep(timeout=min(1, max(0, deadline - time.perf_counter())))
                else:
                    radar.get_range_profile(timeout=min(1, max(0, deadline - time.perf_counter())))
            except TimeoutError:
                continue
            metadata = radar.last_capture_metadata.copy()
            samples.append(metadata)
            radar.log_timing(metadata)
    finally:
        radar.close()
    print(f"[+] {len(samples)} consumed / {radar.completed_sweeps} completed sweeps | "
          f"dropped_packets={radar.dropped_packets} incomplete_sweeps={radar.incomplete_sweeps} "
          f"stale_packets={radar.stale_packets} discarded_sweeps={radar.discarded_sweeps}")
    for key in ("zynq_acquisition_duration_ns", "python_completion_interval_ns",
                "python_receive_duration_ns", "python_queue_age_ns", "python_processing_duration_ns"):
        values = [m[key] / 1e6 for m in samples if m.get(key) is not None]
        if values:
            print(f"[+] {key}: median={np.median(values):.3f} ms "
                  f"p95={np.percentile(values, 95):.3f} ms max={max(values):.3f} ms")


if args.mode != "plot":
    run_measurement()
    raise SystemExit(0)

from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt

# DSP runs independently of the GUI; only the latest processed profile is displayed.
plot_profiles = deque(maxlen=3)
plot_lock = threading.Lock()
processing_stop = threading.Event()
processing_errors = []


def process_profiles():
    averaged = deque(maxlen=SWEEP_AVERAGES)
    try:
        while not processing_stop.is_set():
            try:
                range_axis, rp, sweep_id = radar.get_range_profile(timeout=0.2)
            except TimeoutError:
                continue
            averaged.append(rp)
            if len(averaged) < SWEEP_AVERAGES:
                continue
            rp = np.mean(averaged, axis=0)
            metadata = radar.last_capture_metadata.copy()
            radar.log_timing(metadata)
            with plot_lock:
                plot_profiles.append((range_axis, rp, sweep_id, metadata))
    except Exception as exc:
        if not processing_stop.is_set():
            processing_errors.append(exc)


processing_thread = threading.Thread(target=process_profiles, name="sfcw-dsp", daemon=True)

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
    interpolation="nearest",
    vmin=COLOR_MIN_DB,
    vmax=COLOR_MAX_DB
)

ax_slow.set_title("Range–Slow-Time")
ax_slow.set_xlabel("Range / Fast Time (m)")
ax_slow.set_ylabel("Slow Time (Scan)")
ax_slow.set_xlim(0, 10)

colorbar = fig.colorbar(slow_image, ax=ax_slow)
colorbar.set_label("Magnitude (dB)")

<<<<<<< HEAD
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
=======
plt.tight_layout()
fig.subplots_adjust(bottom=0.14)
color_max_ax = fig.add_axes([0.23, 0.04, 0.55, 0.025])
color_max_slider = Slider(
    color_max_ax,
    "Color max (dB)",
    COLOR_MIN_DB,
    COLOR_MAX_SLIDER_UPPER_DB,
    valinit=COLOR_MAX_DB,
    valstep=1.0,
    valfmt="%0.0f dB"
)
>>>>>>> eabd28fe9e2d8d9a95793bc8cbc0aa712df77da0


def set_color_max(value):
    # Keep normalization nonzero when the slider reaches the fixed -100 dB floor.
    slow_image.set_clim(COLOR_MIN_DB, max(value, COLOR_MIN_DB + 1e-6))
    fig.canvas.draw_idle()


color_max_slider.on_changed(set_color_max)

def update(*_):
    global scan_count

<<<<<<< HEAD
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
=======
    if processing_errors:
        print(f"[-] Processing failed: {processing_errors[0]}")
        plt.close(fig)
        return line, *history_lines, slow_image
    with plot_lock:
        if not plot_profiles:
            return line, *history_lines, slow_image
        range_axis, rp, sweep_id, metadata = plot_profiles.pop()
        plot_profiles.clear()
    plot_start_ns = time.perf_counter_ns()
>>>>>>> eabd28fe9e2d8d9a95793bc8cbc0aa712df77da0

    scan_count += 1
    complex_rp_hist.append(rp.copy())
    if len(complex_rp_hist) > SLOW_TIME_HISTORY:
        complex_rp_hist.pop(0)

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

    print(f"[+] Plot sweep={sweep_id} | preparation={(time.perf_counter_ns() - plot_start_ns) / 1e6:.3f} ms "
          f"age_since_receive={(time.perf_counter_ns() - metadata['python_receive_end_ns']) / 1e6:.3f} ms")
    return line, *history_lines, slow_image

animation = FuncAnimation(
    fig,
    update,
    interval=1000 / args.plot_hz,
    blit=False,
    cache_frame_data=False
)

try:
    processing_thread.start()
    plt.show()
finally:
<<<<<<< HEAD
    radar.close()
=======
    processing_stop.set()
    radar.close()
    processing_thread.join(timeout=1)
>>>>>>> eabd28fe9e2d8d9a95793bc8cbc0aa712df77da0
