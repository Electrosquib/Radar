# Radar

Experimental synthetic-aperture radar (SAR) acquisition and processing code. The repository contains an interactive stepped-frequency continuous-wave (SFCW) workflow, reusable backprojection and autofocus algorithms, an FMCW/GNSS processing pipeline, example data, and KiCad hardware files.

## Main files

- `Processing/Acquisition/SFCW/SAR.py` — interactive SFCW acquisition, rail control, scan persistence, and image generation
- `Processing/Acquisition/SFCW/SFCW.py` — AD936x/Pluto SDR configuration and SFCW range-profile acquisition
- `Processing/Imaging.py` — SAR backprojection
- `Processing/Autofocus.py` — minimum-entropy autofocus (MEA) and phase-gradient autofocus (PGA)
- `Processing/Acquisition/ProcessingFMCW/process_fmcw.py` — recorded FMCW and RTK/GNSS processing CLI
- `Processing/Examples/` — small algorithm experiments and examples

`Processing/Acquisition/SFCW/SAR.py` is the easiest entry point for the complete SFCW workflow. It combines the lower-level, hand-written processing functions into one interactive program.

## Requirements

- Python 3.10 or newer
- NumPy, SciPy, Matplotlib, Pillow, and Numba
- `pyadi-iio` for the SDR
- `pyserial` for the motion rail
- An AD936x-compatible SDR reachable through libiio (the default URI is `usb:`)
- A serial-controlled rail for new acquisitions
- Optional: FFmpeg/FFplay for scene-camera capture on macOS

Create and activate a virtual environment, then install the Python packages:

```sh
python -m venv .venv
```

On macOS/Linux:

```sh
source .venv/bin/activate
python -m pip install numpy scipy matplotlib pillow numba pyadi-iio pyserial soundfile
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install numpy scipy matplotlib pillow numba pyadi-iio pyserial soundfile
```

The SDR also requires the platform-specific libiio drivers and USB permissions supplied by Analog Devices. Verify that the SDR is visible to libiio before starting an acquisition.

## Run the SFCW SAR workflow

First edit the configuration constants near the top of `Processing/Acquisition/SFCW/SAR.py` to match the equipment and desired image:

- `RAIL_PORT`, `RAIL_BAUD`, and the rail movement settings
- `DEVICE_STRING` (for example, `usb:` or an SDR network URI)
- `FMIN`, `FMAX`, and `FS`
- `RAIL_STEPS_TO_CAPTURE` and `RAIL_STEP_INCHES`
- `H_RADAR_FT`, `CROSSRANGE_FT`, `DOWNRANGE_FT`, and `IMAGING_RESOLUTION`

The checked-in `RAIL_PORT` is a macOS device path and will normally need to be changed on Linux or Windows.

From the repository root, run:

```sh
python Processing/Acquisition/SFCW/SAR.py
```

Enter a scene name when prompted. For a new scene:

- `s` starts a scan.
- `b` toggles background calibration for the run.
- `n` lets you choose a different scene name.

For an existing scene:

- `c` continues an interrupted acquisition.
- `g` regenerates all reports from the saved range profiles without connecting to the rail or SDR.
- `r` regenerates reports using a selected slant-range gate.
- `a` corrects the saved rail-position spacing.
- `b` toggles calibration before continuing or generating reports.

Before starting, make sure the rail can move safely through its entire configured travel. Press `Ctrl+C` to interrupt. Completed scans are saved after every rail position, so the same scene can be continued later. When resuming, position the rail at the next unsaved location exactly as the prompt describes.

### Output

Each scene is stored under `Processing/SAR Data/SFCW/<Scene Name>/`. A completed run can contain:

- `range_profiles.npz` — complex profiles, frequency information, and rail positions
- `metadata.json` — scan timestamps, positions, and run status
- `scene.png` — camera image or placeholder
- `bp.png` — backprojected image
- `mea.png` — minimum-entropy autofocus result
- `pga.png` — phase-gradient autofocus result
- `<scene_name>.png` — combined report image

Calibration is stored at `Processing/SAR Data/SFCW/Calibrate/calibration.npy`. Capture it against an empty/background scene using the calibration option, and only apply it to acquisitions made with compatible radar settings.

## Regenerate images from an existing SFCW scan

Run the same interactive program:

```sh
python Processing/Acquisition/SFCW/SAR.py
```

Enter the exact existing scene name and select `g`, or select `r` to restrict processing to a slant-range interval. This path only needs the scene's `range_profiles.npz`; it does not open the rail or SDR.

To change image bounds, resolution, dynamic range, or autofocus iteration counts, edit the corresponding constants near the top of `SAR.py` and regenerate the report.

## Use the processing functions in Python

Run scripts from the repository root and add `Processing` to the import path:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("Processing").resolve()))

import Autofocus
import Imaging

image, crossrange_axis, downrange_axis, complex_image = Imaging.backproject(
    positions=positions,             # antenna positions, in metres
    range_profiles=range_profiles,   # one complex profile per position
    crossrange=(-3.0, 3.0),          # metres
    downrange=(0.0, 6.0),            # metres
    resolution=(200, 200),
    fstart=start_frequency_hz,
    fstop=stop_frequency_hz,
    dr=range_bin_spacing_m,
    output_db=True,
    normalize_db=True,
)
```

See the full `Imaging.backproject()` signature and docstring for coordinate offsets, oversampling, phase sign, calibration, and output orientation. `Autofocus.py` exposes `minimum_entropy_autofocus()`, `parameterized_mea()`, and `phase_gradient_autofocus()` for correcting position or phase errors.

## Process recorded FMCW data with GNSS positions

The FMCW pipeline has its own detailed guide at `Processing/Acquisition/ProcessingFMCW/README.md`. Install its Python dependencies with:

```sh
python -m pip install -r Processing/Acquisition/ProcessingFMCW/requirements.txt
```

RTK position solving additionally requires the RTKLIB programs `convbin` and `rnx2rtkp` on `PATH`. Useful commands from the repository root are:

```sh
python Processing/Acquisition/ProcessingFMCW/process_fmcw.py inventory

python Processing/Acquisition/ProcessingFMCW/process_fmcw.py solve-rtcm \
  --rover-rtcm path/to/rover.rtcm3 \
  --base-rtcm path/to/base.rtcm3 \
  --output Processing/Acquisition/ProcessingFMCW/timestamped_locations.csv

python Processing/Acquisition/ProcessingFMCW/process_fmcw.py process-scans \
  --locations Processing/Acquisition/ProcessingFMCW/timestamped_locations.csv
```

Use `python Processing/Acquisition/ProcessingFMCW/process_fmcw.py --help` and the subcommand-specific `--help` output for input directories, channel selection, radar parameters, and image settings.

## AI use disclosure

Although the important code was human-generated for learning purposes, much of the non-critical boilerplate and tooling was made with ChatGPT. The core algorithms—including MEA, PGA, backprojection, and SFCW processing—are considered important and were hand-coded. Visualization, documentation, rail-control and integration code, and some ports of the MATLAB FMCW radar were created with AI assistance.

This is a long-standing project, so every AI-assisted file may not be identified. The general rule followed in this repository is: code with educational value is written manually; convenience and integration work may use AI assistance. For example, this README.md file was proofread and expounded on with AI. 