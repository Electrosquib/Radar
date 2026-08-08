"""
This is a helper tool to control a rail, compute range profiles using SFCW.py, and perform backprojection and autofocusing using the algorithms placed elsewhere.
Important: this code was made with the assistance of ChatGPT.
"""

import serial
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import Autofocus
import Imaging
import Processing.Acquisition.SFCW.AdjustScanPositions as position_editor
from SFCW import SFCWRadar

RAIL_PORT = "/dev/cu.usbmodem1201"
RAIL_BAUD = 115200
SERIAL_TIMEOUT = 1.0
RAIL_STARTUP_DELAY = 2.0
step_dist = .5
RAIL_STEP_MOVE_TIME = (2.5 * 70 / 255 + 0.08) * step_dist
RAIL_SETTLE_TIME = 0.3
RAIL_STEP_INCHES = .5
RAIL_DIRECTION = "l"
RAIL_STOP = "x"
RAIL_STEPS_TO_CAPTURE = 85

DEVICE_STRING = "usb:"
FMIN = int(3000e6)
FMAX = int(4000e6)
FS = int(20e6)
SWEEP_AVERAGES = 4
SWEEP_RETRIES = 5
SWEEP_RETRY_DELAY = 1.0
CALIBRATION_SAMPLES = 20

DATA_ROOT = PROJECT_ROOT / "SAR Data" / "SFCW"
CALIBRATION_PATH = DATA_ROOT / "Calibrate" / "calibration.npy"
CAMERA_DEVICE = "0:none"

FT = 0.3048
H_RADAR_FT = 6
CROSSRANGE_FT = (-10, 10)
DOWNRANGE_FT = (0, 20)
IMAGING_RESOLUTION = (200, 200)
IMAGE_DYNAMIC_RANGE_DB = 20.0
MEA_ITERATIONS = 20
PGA_ITERATIONS = 3

cal_path = None

SAR_CLI_BANNER = r"""
  ███████╗ █████╗ ██████╗      ██████╗██╗     ██╗
  ██╔════╝██╔══██╗██╔══██╗    ██╔════╝██║     ██║
  ███████╗███████║██████╔╝    ██║     ██║     ██║
  ╚════██║██╔══██║██╔══██╗    ██║     ██║     ██║
  ███████║██║  ██║██║  ██║    ╚██████╗███████╗██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚═════╝╚══════╝╚═╝
                 S A R   C L I
"""


def show_banner():
    cyan = "\033[96m" if sys.stdout.isatty() else ""
    reset = "\033[0m" if cyan else ""
    print(f"{cyan}{SAR_CLI_BANNER}{reset}")
    print("  Stepped-Frequency SAR Acquisition & Imaging")
    print("  " + "─" * 49)

def timestamp_now():
    return datetime.now().astimezone()

def load_metadata(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Could not read existing metadata: {exc}")
        return {}

def write_metadata(path, scene_title, session_start, scans, status, session_stop=None):
    current_time = timestamp_now()
    elapsed_to = session_stop or current_time
    scan_entries = []
    for scan in scans:
        index = int(scan["scan_index"])
        position_in = float(scan["rail_pos_in"])
        scan_entries.append({
            "scan_index": index,
            "name": f"{scene_title} - Position {index + 1:02d}",
            "position_inches": position_in,
            "position_meters": position_in * 0.0254,
            "started_at": scan.get("started_at"),
            "stopped_at": scan.get("stopped_at"),
            "duration_seconds": scan.get("duration_seconds")
        })

    metadata = {
        "scene_title": scene_title,
        "status": status,
        "session": {
            "started_at": session_start.isoformat(),
            "stopped_at": None if session_stop is None else session_stop.isoformat(),
            "elapsed_seconds": (elapsed_to - session_start).total_seconds(),
            "active_scan_seconds": float(sum(
                scan.get("duration_seconds") or 0.0 for scan in scans
            ))
        },
        "scan_count": len(scans),
        "scans": scan_entries
    }
    tmp_path = path.with_name("metadata_tmp.json")
    tmp_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    tmp_path.replace(path)

def prompt_adjust_positions(folder):
    """Collect a new inch spacing and update the saved scan positions."""
    print()
    print("Adjust saved scan positions")
    print("The metadata and range-profile data will stay synchronized.")

    spacing = input("New spacing in inches (or q to cancel): ").strip()
    if spacing.lower() in {"q", "quit", "cancel"}:
        print("Position adjustment cancelled.")
        return
    try:
        if float(spacing) <= 0:
            raise ValueError
    except ValueError:
        print("Spacing must be a number greater than zero.")
        return

    # The editor defaults preserve both the first position and travel direction.
    arguments = [str(folder), "--spacing", spacing]

    print()
    if position_editor.main(arguments) == 0:
        print("Position spacing updated successfully.")


def prompt_range_gate():
    """Ask for an inclusive slant-range gate in feet."""
    print()
    print("Range-gated report generation")
    print("Enter slant range from the radar, not horizontal down range.")
    try:
        minimum_ft = float(input("Minimum range (ft): ").strip())
        maximum_ft = float(input("Maximum range (ft): ").strip())
    except ValueError:
        print("Range limits must be numbers.")
        return None
    if not np.isfinite(minimum_ft) or not np.isfinite(maximum_ft):
        print("Range limits must be finite.")
        return None
    if minimum_ft < 0 or maximum_ft <= minimum_ft:
        print("Maximum range must be greater than a non-negative minimum range.")
        return None
    return minimum_ft, maximum_ft


def prompt_for_scene():
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    calibration_enabled = False
    while True:
        raw_name = input("Scene name: ").strip()
        safe_name = re.sub(r'[\\\\/:*?"<>|]+', "-", raw_name)
        title = " ".join(safe_name.split()).title()
        if not title:
            print("Please enter a scene name.")
            continue
        folder = DATA_ROOT / title
        if folder.exists():
            print(f"Found existing scene: {folder}")
            while True:
                answer = input(
                    "[c] Continue scanning  [g] Generate reports  "
                    "[r] Range-gated reports  [a] Adjust spacing  "
                    f"[b] Calibration: {'ON' if calibration_enabled else 'OFF'}  "
                    "[n] Another scene: "
                ).strip().lower()
                if answer in {"c", "continue"}:
                    slug = re.sub(
                        r"[^a-z0-9]+", "_", title.lower()
                    ).strip("_")
                    return (
                        title, slug, folder, "continue", None,
                        calibration_enabled,
                    )
                if answer in {"g", "generate"}:
                    slug = re.sub(
                        r"[^a-z0-9]+", "_", title.lower()
                    ).strip("_")
                    return (
                        title, slug, folder, "generate", None,
                        calibration_enabled,
                    )
                if answer in {"r", "range", "gate", "range-gated"}:
                    range_gate_ft = prompt_range_gate()
                    if range_gate_ft is None:
                        print()
                        continue
                    slug = re.sub(
                        r"[^a-z0-9]+", "_", title.lower()
                    ).strip("_")
                    return (
                        title, slug, folder, "generate", range_gate_ft,
                        calibration_enabled,
                    )
                if answer in {"a", "adjust"}:
                    prompt_adjust_positions(folder)
                    print()
                    continue
                if answer in {"b", "background", "calibration", "calibrate"}:
                    calibration_enabled = not calibration_enabled
                    state = "enabled" if calibration_enabled else "disabled"
                    print(f"Calibration {state} for this run.")
                    continue
                if answer in {"n", "new", "another"}:
                    break
                print("Please choose c, g, r, a, b, or n.")
            continue
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
        print(f"New scene: {folder}")
        while True:
            answer = input(
                "[s] Start scanning  "
                f"[b] Calibration: {'ON' if calibration_enabled else 'OFF'}  "
                "[n] Another scene: "
            ).strip().lower()
            if answer in {"s", "scan", "start"}:
                folder.mkdir()
                return (
                    title, slug, folder, "new", None,
                    calibration_enabled,
                )
            if answer in {"b", "background", "calibration", "calibrate"}:
                calibration_enabled = not calibration_enabled
                state = "enabled" if calibration_enabled else "disabled"
                print(f"Calibration {state} for this run.")
                continue
            if answer in {"n", "new", "another"}:
                break
            print("Please choose s, b, or n.")

def save_placeholder(path, title, message):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    ax.text(0.5, 0.58, title, ha="center", va="center", fontsize=18)
    ax.text(0.5, 0.42, message, ha="center", va="center", wrap=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

def capture_scene_image(path, title):
    ffplay = shutil.which("ffplay")
    ffmpeg = shutil.which("ffmpeg")
    if not ffplay or not ffmpeg or sys.platform != "darwin":
        save_placeholder(path, title, "Camera preview unavailable")
        print("Camera tools unavailable; saved a placeholder scene image.")
        return

    print("Camera preview opening. Aim the laptop camera, then press q in the preview.")
    try:
        subprocess.run(
            [
                ffplay, "-loglevel", "error", "-window_title", f"{title} Camera",
                "-f", "avfoundation", "-framerate", "30",
                "-video_size", "1280x720", CAMERA_DEVICE
            ],
            check=False
        )
        subprocess.run(
            [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "avfoundation", "-framerate", "30",
                "-video_size", "1280x720", "-i", CAMERA_DEVICE,
                "-vf", r"select=gte(n\,15)", "-frames:v", "1", str(path)
            ],
            check=True
        )
        print("Saved scene image:", path)
    except Exception as exc:
        print(f"Camera capture failed: {exc}")
        save_placeholder(path, title, "Camera capture failed")

def open_rail():
    ser = serial.Serial(RAIL_PORT, RAIL_BAUD, timeout=SERIAL_TIMEOUT)
    time.sleep(RAIL_STARTUP_DELAY)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def send_rail_char(ser, cmd):
    ser.write(cmd.encode("ascii"))
    ser.flush()

def stop_rail(ser):
    send_rail_char(ser, RAIL_STOP)

def move_rail_one_step(ser):
    send_rail_char(ser, RAIL_DIRECTION)
    time.sleep(RAIL_STEP_MOVE_TIME)
    stop_rail(ser)
    time.sleep(RAIL_SETTLE_TIME)

def stack_scans(scans, key):
    return np.stack([s[key] for s in scans], axis=0)

def save_range_profiles(scans, radar, range_axis, scene_title, output_path):
    if len(scans) == 0:
        return

    tmp_file = output_path.with_name("range_profiles_tmp.npz")
    carrier_freqs = np.concatenate([
        freq + radar.bb_freqs for freq in radar.FREQS
    ])
    actual_bw = radar.num_steps * radar.BB_SPACING
    range_res = radar.C / (2 * actual_bw)

    np.savez(
        tmp_file,
        scene_title=scene_title,
        scan_names=np.array([
            f"{scene_title} - Position {int(scan['scan_index']) + 1:02d}"
            for scan in scans
        ]),
        CENTER_FREQS=carrier_freqs,
        LO_FREQS=np.asarray(radar.FREQS),
        BB_FREQS=radar.bb_freqs,
        START_FREQ=carrier_freqs[0],
        RADAR_BW=actual_bw,
        FREQ_STEP=radar.BB_SPACING,
        ACTUAL_BW=actual_bw,
        FS=radar.Fs,
        SDR_BW=radar.Fs,
        RX_BUF_SIZE=radar.BUFF_SIZE,
        TX_GAIN=radar.TX_GAIN,
        RX_LOOPBACK_GAIN=radar.LOOPBACK_GAIN,
        RX_GAIN=radar.RX_GAIN,
        BB_AMP=radar.BB_GAIN,
        SDR_SETTLE_TIME=radar.retune_delay,
        CAPTURE_AVERAGES=radar.CAPTURE_AVERAGES,
        SWEEP_AVERAGES=SWEEP_AVERAGES,
        range_res=range_res,
        range_max=radar.max_range,
        range_axis=range_axis,
        dr=range_res,
        fstart=carrier_freqs[0],
        fstop=carrier_freqs[-1] + radar.BB_SPACING,
        scan_index=np.array([s["scan_index"] for s in scans]),
        rail_pos_in=np.array([s["rail_pos_in"] for s in scans]),
        scan_started_at=np.array([s.get("started_at", "") or "" for s in scans]),
        scan_stopped_at=np.array([s.get("stopped_at", "") or "" for s in scans]),
        scan_duration_seconds=np.array([
            s.get("duration_seconds")
            if s.get("duration_seconds") is not None else np.nan
            for s in scans
        ], dtype=float),
        S_raw=stack_scans(scans, "S_raw"),
        S=stack_scans(scans, "S"),
        range_profiles=stack_scans(scans, "rp"),
        rp=stack_scans(scans, "rp"),
        rp_mag=stack_scans(scans, "rp_mag"),
        rp_db=stack_scans(scans, "rp_db")
    )

    tmp_file.replace(output_path)

def load_range_profiles(path, expected_steps=None):
    if not path.exists():
        return []
    with np.load(path) as data:
        range_profiles = np.asarray(data["range_profiles"])
        if range_profiles.ndim != 2 or (
            expected_steps is not None and range_profiles.shape[1] != expected_steps
        ):
            raise ValueError(
                f"Saved profiles have shape {range_profiles.shape}; "
                f"expected (*, {expected_steps or 'any'})"
            )
        scans = []
        for i in range(range_profiles.shape[0]):
            duration = (
                float(data["scan_duration_seconds"][i])
                if "scan_duration_seconds" in data else np.nan
            )
            rp = range_profiles[i].copy()
            rp_mag = np.abs(rp)
            scans.append({
                "scan_index": int(data["scan_index"][i]),
                "rail_pos_in": float(data["rail_pos_in"][i]),
                "started_at": (
                    str(data["scan_started_at"][i])
                    if "scan_started_at" in data else None
                ),
                "stopped_at": (
                    str(data["scan_stopped_at"][i])
                    if "scan_stopped_at" in data else None
                ),
                "duration_seconds": duration if np.isfinite(duration) else None,
                "S_raw": data["S_raw"][i].copy(),
                "S": data["S"][i].copy(),
                "rp": rp,
                "rp_mag": rp_mag,
                # Recompute this real display field so partial files written
                # by older code with complex rp_db values remain loadable.
                "rp_db": 20 * np.log10(rp_mag + 1e-12)
            })
    return scans

def merge_metadata_into_scans(scans, metadata):
    by_index = {
        int(entry["scan_index"]): entry
        for entry in metadata.get("scans", [])
        if "scan_index" in entry
    }
    for scan in scans:
        entry = by_index.get(int(scan["scan_index"]))
        if entry is None:
            continue
        scan["started_at"] = scan.get("started_at") or entry.get("started_at")
        scan["stopped_at"] = scan.get("stopped_at") or entry.get("stopped_at")
        if scan.get("duration_seconds") is None:
            scan["duration_seconds"] = entry.get("duration_seconds")

def update_plot(scans, fig, ax, img, range_axis):
    if len(scans) == 0:
        img.set_data(np.zeros((1, len(range_axis))))
        img.set_extent([range_axis[0], range_axis[-1], 0, 1])
        ax.set_ylim(0, 1)
    else:
        rp_db_stack = np.asarray([s["rp_db"] for s in scans], dtype=float)
        rail_positions = np.array([s["rail_pos_in"] for s in scans])

        if np.all(np.isfinite(rail_positions)) and len(rail_positions) > 1:
            y_min = rail_positions.min()
            y_max = rail_positions.max()
            img.set_extent([range_axis[0], range_axis[-1], y_min, y_max])
            ax.set_ylim(y_min, y_max)
            ax.set_ylabel("Rail position in")
        else:
            img.set_extent([range_axis[0], range_axis[-1], 0, len(scans)])
            ax.set_ylim(0, len(scans))
            ax.set_ylabel("Scan index")

        img.set_data(rp_db_stack)

    ax.set_title(f"Range profiles ({len(scans)} scans)")
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.05)

def sweep_average_with_retries(radar, averages):
    accumulated = np.zeros_like(radar.S, dtype=np.complex128)
    for average_index in range(averages):
        for attempt in range(1, SWEEP_RETRIES + 1):
            try:
                radar.sweep()
                accumulated += radar.S
                break
            except OSError as exc:
                print(
                    f"SDR I/O error during average {average_index + 1}/{averages}, "
                    f"attempt {attempt}/{SWEEP_RETRIES}: {exc}"
                )
                try:
                    radar.sdr.rx_destroy_buffer()
                except Exception:
                    pass
                time.sleep(SWEEP_RETRY_DELAY)
        else:
            raise RuntimeError(
                f"SDR receive failed {SWEEP_RETRIES} times during "
                f"average {average_index + 1}"
            )
    radar.S = (accumulated / averages).astype(np.complex64)


def prepare_calibration(radar, calibration_path):
    """Load a scene calibration or interactively capture an empty scene."""
    if calibration_path.exists():
        calibration = np.load(calibration_path, allow_pickle=False)
        if calibration.ndim == 1:
            if calibration.shape[0] != radar.num_steps:
                raise ValueError(
                    f"Saved calibration has {calibration.shape[0]} bins; "
                    f"expected {radar.num_steps}"
                )
            backup_path = calibration_path.with_name(
                "calibration_legacy.npy"
            )
            shutil.copy2(calibration_path, backup_path)
            print(
                "Legacy calibration contains only an averaged profile; "
                "a new profile-list calibration is required for envelope "
                "subtraction."
            )
            print(f"Preserved legacy calibration: {backup_path}")
        elif calibration.ndim == 2 and calibration.shape[0] > 0:
            profile_length = calibration.shape[1]
            calibration_profiles = calibration
            if profile_length != radar.num_steps:
                raise ValueError(
                    f"Saved calibration has shape {calibration.shape}; "
                    f"expected (*, {radar.num_steps})"
                )
            if not np.all(np.isfinite(calibration)):
                raise ValueError("Saved calibration contains non-finite values")
            radar.calibration_profiles = calibration_profiles.astype(
                np.complex128, copy=False
            )
            radar.cal = np.mean(radar.calibration_profiles, axis=0)
            print(f"Loaded complex calibration: {calibration_path}")
            return
        else:
            raise ValueError(
                f"Saved calibration must be a profile list; got "
                f"shape {calibration.shape}"
            )

    print()
    print("Background calibration is required before scanning.")
    input("Clear the target from the scene, then press Enter to calibrate: ")
    print(f"Capturing {CALIBRATION_SAMPLES} calibration sweeps...")
    radar.calibrate(
        num_samples=CALIBRATION_SAMPLES,
        output_path=calibration_path,
    )
    print(f"Saved complex calibration: {calibration_path}")
    input("Place the target in the scene, then press Enter to begin scanning: ")


def capture_scan(radar, scan_index, rail_pos_in):
    print()
    print("Capturing scan index:", scan_index)
    print("Rail position in:", rail_pos_in)

    sweep_average_with_retries(radar, SWEEP_AVERAGES)
    # Save the uncalibrated complex profile. Imaging.backproject subtracts the
    # averaged calibration envelope while retaining scan phase for coherent BP.
    range_axis, rp = radar.get_range_profile(plot=False, cal=False)
    S_raw = radar.S.copy()
    S = S_raw - np.mean(S_raw)
    rp_mag = np.abs(rp)
    rp_db = 20 * np.log10(rp_mag + 1e-12)

    scan = {
        "scan_index": scan_index,
        "rail_pos_in": rail_pos_in,
        "S_raw": S_raw,
        "S": S,
        "rp": rp,
        "rp_mag": rp_mag,
        "rp_db": rp_db
    }

    return scan

def make_radar_positions(scans):
    x = np.array([scan["rail_pos_in"] for scan in scans]) * 0.0254
    x -= np.mean(x)
    return np.column_stack((
        x,
        np.zeros(len(scans)),
        np.full(len(scans), H_RADAR_FT * FT)
    ))

def save_sar_image(image, title, path, extent):
    image = np.asarray(image)
    if image.ndim != 2 or not np.any(np.isfinite(image)):
        raise ValueError(f"{title} produced no finite 2D image")
    image = np.nan_to_num(image, nan=-120.0, posinf=0.0, neginf=-120.0)
    peak = float(np.max(image))
    fig, ax = plt.subplots(figsize=(7, 6))
    rendered = ax.imshow(
        image,
        cmap="jet",
        origin="lower",
        extent=extent,
        aspect="auto",
        vmin=peak - IMAGE_DYNAMIC_RANGE_DB,
        vmax=peak
    )
    ax.set_title(title)
    ax.set_xlabel("Cross range (ft)")
    ax.set_ylabel("Down range (ft)")
    fig.colorbar(rendered, ax=ax, label="Magnitude (dB)")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return image

def apply_range_gate(range_profiles, dr, range_gate_ft=None):
    """Return a copy with bins outside an inclusive slant-range gate zeroed."""
    range_profiles = np.asarray(range_profiles)
    if range_gate_ft is None:
        return range_profiles
    if range_profiles.ndim != 2:
        raise ValueError("Range profiles must be a 2D array")
    minimum_ft, maximum_ft = range_gate_ft
    minimum_m = float(minimum_ft) * FT
    maximum_m = float(maximum_ft) * FT
    bin_ranges_m = np.arange(range_profiles.shape[1]) * float(dr)
    keep = (bin_ranges_m >= minimum_m) & (bin_ranges_m <= maximum_m)
    if not np.any(keep):
        raise ValueError(
            f"Range gate {minimum_ft:g}-{maximum_ft:g} ft contains no "
            f"profile bins (bin spacing is {float(dr) / FT:.3g} ft)"
        )
    gated = range_profiles.copy()
    gated[:, ~keep] = 0
    return gated


def generate_sar_images(
    scans, scene_folder, carrier_freqs, dr, range_gate_ft=None,
    calibration_file=None
):
    range_profiles = stack_scans(scans, "rp")
    range_profiles = apply_range_gate(range_profiles, dr, range_gate_ft)
    # range_profiles = range_profiles - np.median(range_profiles, axis=0)
    if range_gate_ft is not None:
        print(
            f"Applied slant-range gate: {range_gate_ft[0]:g} to "
            f"{range_gate_ft[1]:g} ft"
        )
    positions = make_radar_positions(scans)
    carrier_freqs = np.asarray(carrier_freqs)
    frequency_spacing = (
        float(carrier_freqs[1] - carrier_freqs[0])
        if len(carrier_freqs) > 1 else 0.0
    )
    extent = (
        CROSSRANGE_FT[0], CROSSRANGE_FT[1],
        DOWNRANGE_FT[0], DOWNRANGE_FT[1]
    )
    common_parameters = {
        "crossrange": (CROSSRANGE_FT[0] * FT, CROSSRANGE_FT[1] * FT),
        "downrange": (DOWNRANGE_FT[0] * FT, DOWNRANGE_FT[1] * FT),
        "resolution": IMAGING_RESOLUTION,
        "fstart": float(carrier_freqs[0]),
        "fstop": float(carrier_freqs[-1] + frequency_spacing),
        "phase_sign": 1.0,
        "normalize_db": True,
        "flip_lr": False,
        "flip_ud": False,
        "transpose_output": False,
        "os_factor": 1,
        "dr": dr,
        "calibration_file": calibration_file
    }

    results = {}
    output_paths = {
        "bp": scene_folder / "bp.png",
        "mea": scene_folder / "mea.png",
        "pga": scene_folder / "pga.png"
    }

    try:
        print("Generating backprojection image...")
        bp_image, _, _, _ = Imaging.backproject(
            positions=positions,
            range_profiles=range_profiles,
            output_db=True,
            **common_parameters
        )
        results["bp"] = save_sar_image(
            bp_image, "Backprojection (BP)", output_paths["bp"], extent
        )
    except Exception as exc:
        print(f"Backprojection failed: {exc}")
        results["bp"] = None
        save_placeholder(output_paths["bp"], "Backprojection (BP)", str(exc))

    try:
        print("Generating MEA autofocus image...")
        mea_parameters = dict(common_parameters, output_db=False)
        mea_image, _, _, _ = Autofocus.parameterized_mea(
            positions=positions,
            range_profiles=range_profiles,
            base_parameters=mea_parameters,
            stop_entropy_diff=1e-5,
            num_iterations=MEA_ITERATIONS,
            order=6,
            steps=[10] * 4,
            learning_rates=[50, 20, 1, 0.5],
            poly_coeffs=[0] * 4
        )
        results["mea"] = save_sar_image(
            mea_image, "Minimum Entropy Autofocus (MEA)",
            output_paths["mea"], extent
        )
    except Exception as exc:
        print(f"MEA autofocus failed: {exc}")
        results["mea"] = None
        save_placeholder(
            output_paths["mea"], "Minimum Entropy Autofocus (MEA)", str(exc)
        )

    try:
        print("Generating PGA autofocus image...")
        pga_parameters = dict(common_parameters, output_db=True)
        pga_image, _, _ = Autofocus.phase_gradient_autofocus(
            positions=positions,
            range_profiles=range_profiles,
            base_parameters=pga_parameters,
            num_iterations=PGA_ITERATIONS
        )
        results["pga"] = save_sar_image(
            pga_image, "Phase Gradient Autofocus (PGA)",
            output_paths["pga"], extent
        )
    except Exception as exc:
        print(f"PGA autofocus failed: {exc}")
        results["pga"] = None
        save_placeholder(
            output_paths["pga"], "Phase Gradient Autofocus (PGA)", str(exc)
        )

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, key, title in zip(
        axes,
        ("bp", "mea", "pga"),
        ("Backprojection (BP)", "MEA Autofocus", "PGA Autofocus")
    ):
        image = results[key]
        if image is None:
            ax.text(0.5, 0.5, f"{title}\nFailed", ha="center", va="center")
            ax.axis("off")
            continue
        peak = float(np.max(image))
        ax.imshow(
            image, cmap="jet", origin="lower", extent=extent,
            aspect="auto", vmin=peak - IMAGE_DYNAMIC_RANGE_DB, vmax=peak
        )
        ax.set_title(title)
        ax.set_xlabel("Cross range (ft)")
        ax.set_ylabel("Down range (ft)")
    fig.tight_layout()
    return fig, output_paths

def save_composition(scene_path, output_paths, scene_title, output_path):
    panels = [
        (scene_path, "Scene"),
        (output_paths["bp"], "Backprojection (BP)"),
        (output_paths["mea"], "MEA Autofocus"),
        (output_paths["pga"], "PGA Autofocus")
    ]
    fig, axes = plt.subplots(1, 4, figsize=(24, 6))
    for ax, (path, title) in zip(axes, panels):
        try:
            ax.imshow(plt.imread(path))
        except Exception as exc:
            ax.text(0.5, 0.5, f"Unavailable\n{exc}", ha="center", va="center")
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle(scene_title, fontsize=20)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

def generate_existing_reports(
    scene_title, scene_folder, profiles_path, scene_path, composition_path,
    range_gate_ft=None, calibration_file=None
):
    if not profiles_path.exists():
        print(f"No partial scan data found at {profiles_path}")
        return
    scans = load_range_profiles(profiles_path)
    if not scans:
        print("No completed scan positions are available.")
        return
    with np.load(profiles_path) as data:
        carrier_freqs = np.asarray(data["CENTER_FREQS"])
        dr = float(data["dr"])
    if not scene_path.exists():
        save_placeholder(scene_path, scene_title, "Scene photograph unavailable")

    print(f"Generating reports from {len(scans)} completed positions...")
    triptych, output_paths = generate_sar_images(
        scans, scene_folder, carrier_freqs, dr,
        range_gate_ft=range_gate_ft,
        calibration_file=calibration_file,
    )
    save_composition(
        scene_path, output_paths, scene_title, composition_path
    )
    print("Saved reports in:", scene_folder)
    plt.show()
    plt.close(triptych)

def main():
    rail = None
    radar = None
    show_banner()
    (
        scene_title, scene_slug, scene_folder, action, range_gate_ft,
        calibration_enabled,
    ) = prompt_for_scene()
    scene_path = scene_folder / "scene.png"
    profiles_path = scene_folder / "range_profiles.npz"
    metadata_path = scene_folder / "metadata.json"
    calibration_path = CALIBRATION_PATH
    composition_path = scene_folder / f"{scene_slug}.png"
    if action == "generate":
        generate_existing_reports(
            scene_title, scene_folder, profiles_path,
            scene_path, composition_path,
            range_gate_ft=range_gate_ft,
            calibration_file=(
                calibration_path if calibration_enabled else None
            ),
        )
        return

    resume = action == "continue"
    existing_metadata = load_metadata(metadata_path) if resume else {}
    try:
        session_start = datetime.fromisoformat(
            existing_metadata["session"]["started_at"]
        )
    except (KeyError, TypeError, ValueError):
        session_start = timestamp_now()
    session_stop = None
    run_status = "in_progress"
    scans = None if resume else []
    if scans is not None:
        write_metadata(
            metadata_path, scene_title, session_start, scans, run_status
        )
    if not resume or not scene_path.exists():
        capture_scene_image(scene_path, scene_title)

    try:
        rail = open_rail()
        radar = SFCWRadar(
            device_string=DEVICE_STRING,
            Fmin=FMIN,
            Fmax=FMAX,
            Fs=FS,
            verbose=False
        )
        try:
            # print("Optimized gains:", radar.auto_optimize_gains())
            pass
        except OSError as exc:
            print(f"Gain optimization skipped after SDR I/O error: {exc}")
            try:
                radar.sdr.rx_destroy_buffer()
            except Exception:
                pass
        if calibration_enabled:
            calibration_path.parent.mkdir(parents=True, exist_ok=True)
            prepare_calibration(radar, calibration_path)
        else:
            print("Calibration disabled; using uncalibrated complex profiles.")
        range_axis = (
            np.arange(radar.num_steps)
            * radar.C
            / (2 * radar.num_steps * radar.BB_SPACING)
        )
        actual_bw = radar.num_steps * radar.BB_SPACING
        range_res = radar.C / (2 * actual_bw)

        print("Frequency steps:", radar.num_steps)
        print("Actual BW MHz:", actual_bw / 1e6)
        print("Range resolution m:", range_res)
        print("Max unambiguous range m:", radar.max_range)

        scans = load_range_profiles(profiles_path, radar.num_steps) if resume else scans
        merge_metadata_into_scans(scans, existing_metadata)
        write_metadata(
            metadata_path, scene_title, session_start, scans, run_status
        )
        start_step = len(scans)
        capture_current_position = False
        if start_step:
            print(f"Loaded {start_step} completed positions from {profiles_path}")
            if start_step < RAIL_STEPS_TO_CAPTURE:
                expected_position = -(start_step + 1) * RAIL_STEP_INCHES
                answer = input(
                    f"Is the rail already at the next unsaved position "
                    f"({expected_position:.1f} in)? [y/N]: "
                ).strip().lower()
                if answer != "y":
                    print("Resume cancelled. Position the rail, then run again.")
                    session_stop = timestamp_now()
                    run_status = "resume_cancelled"
                    write_metadata(
                        metadata_path, scene_title, session_start, scans,
                        run_status, session_stop
                    )
                    return
                capture_current_position = True

        plt.ion()
        fig, ax = plt.subplots(figsize=(11, 6))
        img = ax.imshow(
            np.zeros((1, radar.num_steps)),
            aspect="auto",
            origin="lower",
            cmap="jet",
            extent=[range_axis[0], range_axis[-1], 0, 1],
            vmin=-60,
            vmax=0
        )

        plt.colorbar(img, ax=ax, label="Magnitude dB")
        ax.set_xlabel("Range m")
        ax.set_xlim(0, radar.max_range)
        update_plot(scans, fig, ax, img, range_axis)

        for rail_step in range(start_step, RAIL_STEPS_TO_CAPTURE):
            rail_pos_in = -(rail_step + 1) * RAIL_STEP_INCHES

            if capture_current_position:
                print(
                    f"Capturing current rail position "
                    f"{rail_step + 1}/{RAIL_STEPS_TO_CAPTURE}"
                )
                capture_current_position = False
            else:
                print()
                print(f"Moving rail step {rail_step + 1}/{RAIL_STEPS_TO_CAPTURE}")
                move_rail_one_step(rail)

            scan_started = timestamp_now()
            scan_timer = time.perf_counter()
            scan = capture_scan(radar, rail_step, rail_pos_in)
            scan_stopped = timestamp_now()
            scan["started_at"] = scan_started.isoformat()
            scan["stopped_at"] = scan_stopped.isoformat()
            scan["duration_seconds"] = time.perf_counter() - scan_timer
            scans.append(scan)
            save_range_profiles(
                scans, radar, range_axis, scene_title, profiles_path
            )
            write_metadata(
                metadata_path, scene_title, session_start, scans, run_status
            )
            update_plot(scans, fig, ax, img, range_axis)

            print(
                f"Saved {scene_title} - Position {rail_step + 1:02d} "
                f"to {profiles_path}"
            )

        print()
        print("Generating SAR imagery...")
        carrier_freqs = np.concatenate([
            freq + radar.bb_freqs for freq in radar.FREQS
        ])
        triptych, output_paths = generate_sar_images(
            scans, scene_folder, carrier_freqs, range_res,
            calibration_file=(
                calibration_path if calibration_enabled else None
            ),
        )
        save_composition(
            scene_path, output_paths, scene_title, composition_path
        )
        session_stop = timestamp_now()
        run_status = "completed"
        write_metadata(
            metadata_path, scene_title, session_start, scans,
            run_status, session_stop
        )
        print("Saved scene folder:", scene_folder)
        plt.ioff()
        plt.show()
        plt.close(triptych)
        print("Done.")

    except KeyboardInterrupt:
        print()
        print("Stopped by user.")
        session_stop = timestamp_now()
        run_status = "interrupted"
        if scans is not None:
            write_metadata(
                metadata_path, scene_title, session_start, scans,
                run_status, session_stop
            )

    except Exception:
        session_stop = timestamp_now()
        run_status = "failed"
        if scans is not None:
            write_metadata(
                metadata_path, scene_title, session_start, scans,
                run_status, session_stop
            )
        raise

    finally:
        if rail is not None:
            try:
                stop_rail(rail)
                rail.close()
            except Exception:
                pass

        if radar is not None:
            try:
                radar.sdr.tx_destroy_buffer()
                radar.sdr.rx_destroy_buffer()
            except Exception:
                pass

if __name__ == "__main__":
    main()
