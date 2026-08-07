import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.signal.windows import hann, kaiser
from scipy.io import wavfile
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
from PIL import Image
from numba import njit, prange

# CONSTANTS:
c = 299792458 # m/s


@njit(fastmath=True)
def map_value(x, in_min, in_max, out_min, out_max):
    val = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    if np.isnan(val): val = 0
    return val

@njit(fastmath=True)
def interp_rp(k, rp):
    if k < 0 or k >= len(rp) - 1:
        return 0j
    k0 = int(np.floor(k))
    a = k - k0
    val =  (1 - a) * rp[k0] + a * rp[k0 + 1]
    return val
    

def plot_3d(x_grid, y_grid, z_grid, pos):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    print(np.min(x_grid), np.max(x_grid))
    x = pos[:, 0]
    y = pos[:, 1]
    z = pos[:, 2]
    ax.set_xlim(np.min(x_grid), np.max(x_grid))
    ax.set_ylim(np.min(y_grid), np.max(y_grid))
    ax.set_zlim(np.min(z_grid), np.max(z_grid))
    ax.plot(x, y, z)
    ax.set_xlabel("X (crossrange)")
    ax.set_ylabel("Y (downrange)")
    ax.set_zlabel("Z (altitude)")
    plt.title("SAR Trajectory")
    plt.show()

@njit(parallel=True, fastmath=True)
def _backproject_core(
    positions,
    range_profiles,
    dr,
    phase_error=None,                    # Must be same length as positions and range_profiles. Given in radians.
    crossrange=(0.0, 5.0),
    downrange=(0.0, 9.0),
    resolution=(100, 100),
    fstart=2280e6,
    fstop=2580e6,
    phase_sign=-1.0,
    output_db=True,
    normalize_db=True,
    flip_lr=True,
    flip_ud=False,
    transpose_output=True,
    os_factor=8,
    x_scale=1,
    x_offset=0,
    y_offset=0,
    z_offset=0,
    cable_off_ft=0.0,
    pga=False
):
    """
    Autofocus parameter vector:
        x_scale   = aperture distance scale error
        x_offset  = aperture origin error
        y_offset  = downrange offset error
        z_offset  = radar height error
        r0_m      = range/cable delay offset
    """
    B = fstop - fstart
    fc = (fstart + fstop) / 2.0

    x_grid = np.linspace(crossrange[0], crossrange[1], resolution[0])
    y_grid = np.linspace(downrange[0], downrange[1], resolution[1])
    if phase_error is None:
        phase_error = np.zeros(positions.shape[0])
    elif len(phase_error) != positions.shape[0]:
        raise ValueError("Length of phase_error must be 0 or equal to number of positions and range_profiles.")
    phase_hist = np.zeros((resolution[1], resolution[0], range_profiles.shape[0]), np.complex128)
    img = np.zeros((resolution[1], resolution[0]), np.complex128)
    for yi in prange(len(y_grid)):
        y = y_grid[yi]

        for xi in range(len(x_grid)):
            x = x_grid[xi]
            for i in range(positions.shape[0]):
                xc = x_scale * positions[i, 0] + x_offset
                yc = positions[i, 1] + y_offset
                zc = positions[i, 2] + z_offset

                dx = x - xc
                dy = y - yc
                dz = -zc

                d = np.sqrt(dx * dx + dy * dy + dz * dz)
                k = (d) / dr
                s = interp_rp(k, range_profiles[i])
                val = s * np.exp(phase_sign * 1j * 4.0 * np.pi * fc * d / c - 1j * phase_error[i])

                if pga is True:
                    phase_hist[xi, yi, i] = val
                img[yi, xi] += val

    img = np.abs(img)
    img = np.nan_to_num(img, nan=0.0, posinf=0.0, neginf=0.0)

    if output_db:
        peak = np.max(img)
        if normalize_db:
            if peak > 0:
                img = 20.0 * np.log10(img / peak + 1e-12)
            else:
                img = np.full_like(img, -120.0)
        else:
            img = 20.0 * np.log10(img + 1e-12)
        img = np.nan_to_num(img, nan=-120.0, posinf=0.0, neginf=-120.0)

    if flip_lr:
        img = np.fliplr(img)
        phase_hist = np.fliplr(phase_hist)
    if flip_ud:
        img = np.flipud(img)
        phase_hist = np.flipud(phase_hist)

    if transpose_output:
        img = img.T
        axis_cross = y_grid
        axis_down = x_grid
    else:
        axis_cross = x_grid
        axis_down = y_grid

    return img, axis_cross, axis_down, phase_hist


def _calibrated_profiles(range_profiles, calibration_file):
    """Subtract an averaged calibration envelope while preserving scan phase."""
    profiles = np.asarray(range_profiles)
    if profiles.ndim != 2:
        raise ValueError("range_profiles must be a 2D array")
    if calibration_file is None:
        return profiles

    if isinstance(calibration_file, (str, bytes)) or hasattr(
        calibration_file, "__fspath__"
    ):
        calibration_profiles = np.load(calibration_file, allow_pickle=False)
    else:
        calibration_profiles = np.asarray(calibration_file)

    if calibration_profiles.ndim == 1:
        # Accept legacy files containing one complex averaged profile.
        calibration_envelope = np.abs(calibration_profiles)
    elif calibration_profiles.ndim == 2 and calibration_profiles.shape[0] > 0:
        calibration_envelope = np.mean(
            np.abs(calibration_profiles), axis=0
        )
    else:
        raise ValueError(
            "Calibration must contain one profile or a non-empty list of profiles"
        )
    if calibration_envelope.shape != (profiles.shape[1],):
        raise ValueError(
            f"Calibration profile has {calibration_envelope.size} bins; "
            f"scan profiles have {profiles.shape[1]} bins"
        )
    if not np.all(np.isfinite(calibration_envelope)):
        raise ValueError("Calibration contains non-finite values")

    scan_envelope = np.abs(profiles)
    corrected_envelope = np.maximum(
        scan_envelope - calibration_envelope[None, :], 0.0
    )
    # Retain the measured phase so the aperture sum remains coherent.
    scan_phase = np.zeros_like(profiles, dtype=np.complex128)
    nonzero = scan_envelope > 0
    scan_phase[nonzero] = profiles[nonzero] / scan_envelope[nonzero]
    corrected = corrected_envelope * scan_phase

    # Preserve explicit zero bins created by range gating exactly.
    active_bins = np.any(profiles != 0, axis=0)
    corrected[:, ~active_bins] = 0
    return corrected


def backproject(
    positions,
    range_profiles,
    dr,
    phase_error=None,
    crossrange=(0.0, 5.0),
    downrange=(0.0, 9.0),
    resolution=(100, 100),
    fstart=2280e6,
    fstop=2580e6,
    phase_sign=-1.0,
    output_db=True,
    normalize_db=True,
    flip_lr=True,
    flip_ud=False,
    transpose_output=True,
    os_factor=8,
    x_scale=1,
    x_offset=0,
    y_offset=0,
    z_offset=0,
    cable_off_ft=0.0,
    pga=False,
    calibration_file=None,
):
    """Coherently backproject, optionally subtracting a calibration envelope."""
    corrected_profiles = _calibrated_profiles(
        range_profiles, calibration_file
    )
    return _backproject_core(
        positions=positions,
        range_profiles=corrected_profiles,
        dr=dr,
        phase_error=phase_error,
        crossrange=crossrange,
        downrange=downrange,
        resolution=resolution,
        fstart=fstart,
        fstop=fstop,
        phase_sign=phase_sign,
        output_db=output_db,
        normalize_db=normalize_db,
        flip_lr=flip_lr,
        flip_ud=flip_ud,
        transpose_output=transpose_output,
        os_factor=os_factor,
        x_scale=x_scale,
        x_offset=x_offset,
        y_offset=y_offset,
        z_offset=z_offset,
        cable_off_ft=cable_off_ft,
        pga=pga,
    )
