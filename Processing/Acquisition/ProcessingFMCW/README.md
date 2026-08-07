# ProcessingFMCW

This pipeline turns paired base/rover RTCM3 observations into timestamped
locations, recovers each radar pulse time from the recorded PRF rising edge,
and uses the repository's existing `Imaging.backproject` implementation.

## Requirements

- Python packages in `requirements.txt`
- RTKLIB command-line programs `convbin` and `rnx2rtkp` on `PATH`

## 1. Inspect the recordings

```sh
python3 "SAR Data/ProcessingFMCW/process_fmcw.py" inventory
```

The current scan sidecars are dated 2026-05-07. A rover RTCM3 stream covering
that UTC interval is required; the rover streams currently in this workspace
begin later, so they cannot produce positions for these scans.

## 2. Solve a matching RTCM3 pair

Inputs can be extracted files, ZIP files containing exactly one non-empty
RTCM3 stream, or an explicit ZIP member written as `archive.zip!member.rtcm3`.

```sh
python3 "SAR Data/ProcessingFMCW/process_fmcw.py" solve-rtcm \
  --rover-rtcm "SAR Data/Rover/ROVER.rtcm3" \
  --base-rtcm "SAR Data/Base/BASE.rtcm3" \
  --output "SAR Data/ProcessingFMCW/timestamped_locations.csv"
```

The output contains UTC, latitude, longitude, ellipsoidal height, RTK quality,
satellite count, and position uncertainty for every rover solution epoch.

## 3. Process scans

```sh
python3 "SAR Data/ProcessingFMCW/process_fmcw.py" process-scans \
  --locations "SAR Data/ProcessingFMCW/timestamped_locations.csv"
```

If an `edges_*.csv` contains edges, those sample/time pairs are used. If it is
empty and only start/stop timing exists, rising edges are detected directly on
the WAV channel given by `combined_edge_channel`/`edge_channel` in the metadata.
If that recorded channel is silent, the active pulse-train channel is detected
automatically. Override it strictly with `--prf-channel N`. Channels are
zero-based; radar defaults to channel 1 to match the existing processor.

Each successful scan writes:

- `*_pulse_locations.csv`: timestamp and interpolated ENU antenna position per pulse
- `*_backprojection.npz`: image, axes, antenna positions, pulse times, and range spacing
- `*_backprojection.png`: rendered normalized-dB image

Use `--wav PATH` to process one recording. Run `--help` on either subcommand for
channel, waveform, radar frequency, image-grid, and output options.
