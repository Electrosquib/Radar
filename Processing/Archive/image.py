"""
Backprojection + optional MEA using NPZ SAR data with linear rail positions.

Assumes SAR moved STEP_INCHES per scan.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import time

import Imaging
import Autofocus

NPZ_FOLDER = Path("scans0")
NPZ_FILE = None

RESOLUTION = (3000, 3000)
DYNAMIC_RANGE_DB = 10.0

STEP_INCHES = 1.0
STEP_M = STEP_INCHES * 0.0254

FT = 0.3048
C = 299_792_458.0

FSTART = 2.28e9
FSTOP = 2.58e9
IMAGE_OVERSAMPLE = 8
CALIBRATION_OFFSET_FT = 0.0
H_RADAR_FT = 6.0

CROSSRANGE_FT = (-10, 10)
DOWNRANGE_FT = (0, 25)


def latest_npz(folder):
    files = sorted(folder.glob("*.npz"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise FileNotFoundError(f"No .npz files found in {folder}")
    return files[-1]


def load_npz_data(filename):
    data = np.load(filename, allow_pickle=True)

    for key in ["range_profiles", "rp", "profiles", "S"]:
        if key in data:
            rp = data[key]
            break
    else:
        raise KeyError(f"No range profile key found. Available keys: {list(data.keys())}")

    rp = np.asarray(rp)

    if rp.ndim != 2:
        raise ValueError(f"Expected range profiles to be 2D, got shape {rp.shape}")

    fstart = float(data["fstart"]) if "fstart" in data else FSTART
    fstop = float(data["fstop"]) if "fstop" in data else FSTOP
    os_factor = int(data["os_factor"]) if "os_factor" in data else IMAGE_OVERSAMPLE
    calibration_offset_ft = float(data["calibration_offset_ft"]) if "calibration_offset_ft" in data else CALIBRATION_OFFSET_FT
    h_radar_ft = float(data["h_radar_ft"]) if "h_radar_ft" in data else H_RADAR_FT

    if "dr" in data:
        dr = float(data["dr"])
    else:
        bandwidth = fstop - fstart
        dr = C / (2 * bandwidth * os_factor)

    return rp, fstart, fstop, dr, os_factor, calibration_offset_ft, h_radar_ft, data


def make_linear_positions(num_scans, step_m=STEP_M, h_radar_ft=H_RADAR_FT):
    x = (np.arange(num_scans) - (num_scans - 1) / 2) * step_m
    y = np.zeros(num_scans)
    z = np.full(num_scans, h_radar_ft * FT)
    return np.column_stack((x, y, z))


def main():
    filename = Path(NPZ_FILE) if NPZ_FILE else latest_npz(NPZ_FOLDER)
    print(f"Loading {filename}")

    rp, fstart, fstop, dr, os_factor, calibration_offset_ft, h_radar_ft, raw = load_npz_data(filename)

    positions = make_linear_positions(
        num_scans=rp.shape[0],
        step_m=STEP_M,
        h_radar_ft=h_radar_ft
    )

    print(f"Range profiles: {rp.shape}")
    print(f"Positions: {positions.shape}")
    print(f"Rail step: {STEP_INCHES:.3f} in = {STEP_M:.6f} m")
    print(f"Synthetic aperture length: {(rp.shape[0] - 1) * STEP_M:.3f} m")
    print(f"fstart: {fstart / 1e9:.3f} GHz")
    print(f"fstop: {fstop / 1e9:.3f} GHz")
    print(f"dr: {dr:.6f} m")

    start_ns = time.perf_counter_ns()

    img_bp, crossrange_axis, downrange_axis, _ = Imaging.backproject(
        positions=positions,
        range_profiles=rp,
        crossrange=(CROSSRANGE_FT[0] * FT, CROSSRANGE_FT[1] * FT),
        downrange=(DOWNRANGE_FT[0] * FT, DOWNRANGE_FT[1] * FT),
        resolution=RESOLUTION,
        fstart=fstart,
        fstop=fstop,
        phase_sign=1.0,
        output_db=True,
        normalize_db=True,
        flip_lr=False,
        flip_ud=False,
        transpose_output=False,
        os_factor=os_factor,
        dr=dr,
        x_scale=1.0,
        x_offset=0.0,
        y_offset=0.0,
        z_offset=0.0,
        cable_off_ft=calibration_offset_ft
    )

    end_ns = time.perf_counter_ns()
    print(f"Backprojection took {(end_ns - start_ns) / 1e9:.2f} seconds")

    if not np.all(np.isfinite(img_bp)):
        print("Warning: image contains NaN or Inf values")
        img_bp = np.nan_to_num(img_bp, nan=-120.0, posinf=0.0, neginf=-120.0)

    peak = np.max(img_bp)

    extent = (
        crossrange_axis[0] / FT,
        crossrange_axis[-1] / FT,
        downrange_axis[0] / FT,
        downrange_axis[-1] / FT
    )

    fig, ax = plt.subplots(figsize=(13, 5))

    im = ax.imshow(
        img_bp,
        cmap="jet",
        origin="lower",
        extent=extent,
        aspect="auto",
        vmin=peak - DYNAMIC_RANGE_DB,
        vmax=peak
    )

    ax.set_xlabel("Cross range (ft)")
    ax.set_ylabel("Down range (ft)")
    ax.set_title("Backprojection")
    ax.grid(False)

    fig.colorbar(im, ax=ax, label="Magnitude (dB)")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()