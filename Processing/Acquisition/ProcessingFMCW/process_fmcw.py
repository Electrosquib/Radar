#!/usr/bin/env python3
"""RTCM3-to-position and timestamp-aware FMCW SAR processing pipeline.

RTCM3 observations are converted/solved with RTKLIB (``convbin`` and
``rnx2rtkp``).  Radar pulse times come from a sidecar edge CSV when populated,
or are recovered from rising edges on the WAV PRF channel.  The solved GNSS
trajectory is interpolated at those pulse times and passed to the repository's
existing ``Imaging.backproject`` implementation.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
SAR_DATA = HERE.parent
REPO_ROOT = SAR_DATA.parent
DEFAULT_SCANS = SAR_DATA / "Scans"
DEFAULT_BASE = SAR_DATA / "Base"
DEFAULT_ROVER = SAR_DATA / "Rover"


@dataclass(frozen=True)
class Scan:
    wav: Path
    metadata: dict[str, str]
    meta_path: Path | None
    edge_path: Path | None

    @property
    def start(self) -> datetime:
        value = self.metadata.get("utc_start_iso")
        if value:
            return parse_utc(value)
        stamp = scan_key(self.wav)
        if stamp is None:
            raise ValueError(f"No UTC timestamp is available for {self.wav.name}")
        return datetime.strptime(stamp, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)

    @property
    def stop(self) -> datetime:
        value = self.metadata.get("utc_stop_iso")
        if value:
            return parse_utc(value)
        _, _, fs, frames = wav_parameters(self.wav)
        seconds = frames / fs
        return datetime.fromtimestamp(self.start.timestamp() + seconds, timezone.utc)


@dataclass(frozen=True)
class Position:
    utc_unix: float
    latitude_deg: float
    longitude_deg: float
    height_m: float
    quality: int = 0
    satellites: int = 0
    sigma_e_m: float = math.nan
    sigma_n_m: float = math.nan
    sigma_u_m: float = math.nan


def parse_utc(value: str) -> datetime:
    value = value.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def wav_parameters(path: Path) -> tuple[int, int, int, int]:
    """Return channels, sample width, rate, frames, including unfinalized PCM WAVs."""
    try:
        with wave.open(str(path), "rb") as wav:
            return wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
    except wave.Error:
        header = path.read_bytes()[:44]
        if len(header) < 44 or header[:4] != b"RIFF" or header[8:12] != b"WAVE":
            raise ValueError(f"Invalid WAV header: {path}")
        audio_format, channels, fs, _, block_align, bits = struct.unpack_from("<HHIIHH", header, 20)
        if audio_format != 1 or bits not in (8, 16, 24, 32):
            raise ValueError(f"Unsupported unfinalized WAV format: {path}")
        width = bits // 8
        frames = max(0, path.stat().st_size - 44) // block_align
        return channels, width, fs, frames


def read_metadata(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    section = ""
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
        elif "=" in line:
            key, value = line.split("=", 1)
            # Stop fields are useful without requiring callers to know sections.
            result[key.strip()] = value.strip()
            result[f"{section}.{key.strip()}" if section else key.strip()] = value.strip()
    return result


def scan_key(path: Path) -> str | None:
    # Handles combined_audio_YYYYMMDD_HHMMSS_UTC.wav and sidecar equivalents.
    parts = path.stem.split("_")
    for i, part in enumerate(parts[:-1]):
        if len(part) == 8 and part.isdigit() and i + 1 < len(parts):
            candidate = f"{part}_{parts[i + 1]}"
            if len(parts[i + 1]) == 6 and parts[i + 1].isdigit():
                return candidate
    return None


def discover_scans(folder: Path) -> list[Scan]:
    scans: list[Scan] = []
    for wav in sorted(folder.glob("*.wav")):
        key = scan_key(wav)
        # Ignore unrelated/legacy WAVs that have no UTC key or sidecars.
        if key is None:
            continue
        meta = folder / f"meta_{key}_UTC.txt" if key else None
        metadata = read_metadata(meta) if meta and meta.exists() else {}
        edge_name = metadata.get("edge_file")
        edge = folder / edge_name if edge_name else (folder / f"edges_{key}_UTC.csv" if key else None)
        scans.append(Scan(wav, metadata, meta if meta and meta.exists() else None,
                          edge if edge and edge.exists() else None))
    return scans


def list_rtcm(folder: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for path in sorted(folder.rglob("*.rtcm3")):
        rows.append((str(path), path.stat().st_size, "file"))
    for archive in sorted(folder.glob("*.zip")):
        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():
                if info.filename.lower().endswith(".rtcm3"):
                    rows.append((f"{archive}!{info.filename}", info.file_size, "zip"))
    return rows


def command_inventory(args: argparse.Namespace) -> int:
    scans = discover_scans(args.scans)
    print(f"Scans: {len(scans)}")
    for scan in scans:
        print(f"  {scan.start.isoformat()} .. {scan.stop.isoformat()}  {scan.wav.name}")
    for label, folder in (("Base RTCM3", args.base), ("Rover RTCM3", args.rover)):
        rows = list_rtcm(folder)
        usable = [row for row in rows if row[1] > 0]
        print(f"{label}: {len(usable)} non-empty of {len(rows)} streams")
        for name, size, _ in usable:
            print(f"  {size:>10}  {name}")
    if scans:
        scan_days = {scan.start.date() for scan in scans}
        rover_names = " ".join(name for name, size, _ in list_rtcm(args.rover) if size)
        missing = [day for day in sorted(scan_days) if day.strftime("%Y-%m-%d") not in rover_names]
        if missing:
            print("WARNING: no rover RTCM3 filename matches scan date(s): " +
                  ", ".join(map(str, missing)), file=sys.stderr)
    return 0


def materialize_rtcm(spec: str, work: Path, role: str) -> Path:
    """Return an ordinary RTCM3 path from a file or archive!member spec."""
    if "!" in spec:
        archive_name, member = spec.split("!", 1)
        archive = Path(archive_name).expanduser().resolve()
        target = work / f"{role}_{Path(member).name}"
        with zipfile.ZipFile(archive) as zf, zf.open(member) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return target
    source = Path(spec).expanduser().resolve()
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as zf:
            members = [i for i in zf.infolist()
                       if i.filename.lower().endswith(".rtcm3") and i.file_size > 0]
            if len(members) != 1:
                raise ValueError(f"{source} has {len(members)} non-empty RTCM3 members; use archive.zip!member")
            target = work / f"{role}_{Path(members[0].filename).name}"
            with zf.open(members[0]) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            return target
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError(f"RTCM3 input is missing or empty: {source}")
    return source


def run_checked(command: Sequence[str]) -> None:
    print("+ " + " ".join(map(str, command)))
    subprocess.run(list(map(str, command)), check=True)


def convert_rtcm(rtcm: Path, prefix: Path, convbin: str) -> tuple[Path, list[Path]]:
    obs = prefix.with_suffix(".obs")
    nav = prefix.with_suffix(".nav")
    gnav = prefix.with_suffix(".gnav")
    hnav = prefix.with_suffix(".hnav")
    qnav = prefix.with_suffix(".qnav")
    lnav = prefix.with_suffix(".lnav")
    run_checked([convbin, "-r", "rtcm3", "-od", "-os", "-oi", "-ot",
                 "-o", obs, "-n", nav, "-g", gnav, "-h", hnav,
                 "-q", qnav, "-l", lnav, rtcm])
    if not obs.exists() or obs.stat().st_size == 0:
        raise RuntimeError(f"convbin did not produce observations from {rtcm}")
    navs = [p for p in (nav, gnav, hnav, qnav, lnav) if p.exists() and p.stat().st_size]
    if not navs:
        raise RuntimeError(f"convbin did not produce navigation data from {rtcm}")
    return obs, navs


def write_rtklib_config(path: Path) -> None:
    path.write_text("""# RTKLIB options for timestamped rover trajectory
pos1-posmode       =kinematic
pos1-frequency     =l1+l2
pos1-soltype       =forward
pos1-elmask        =15
pos2-armode        =continuous
pos2-gloarmode     =on
pos2-bdsarmode     =on
pos2-arfilter      =on
out-solformat      =llh
out-outhead        =on
out-outopt         =on
out-timesys        =utc
out-timeform       =hms
out-timendec       =6
out-degform        =deg
out-height         =ellipsoidal
out-fieldsep       =,
ant2-postype       =rinexhead
""")


def parse_rtklib_pos(path: Path) -> list[Position]:
    rows: list[Position] = []
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("%") or line.startswith("#"):
            continue
        fields = [x.strip() for x in line.split(",")]
        if len(fields) < 6:
            fields = line.split()
            if len(fields) < 7:
                continue
            date, clock, rest = fields[0], fields[1], fields[2:]
        else:
            first = fields[0].split()
            if len(first) == 2:
                date, clock, rest = first[0], first[1], fields[1:]
            else:
                continue
        try:
            stamp = parse_utc(f"{date.replace('/', '-')}T{clock}").timestamp()
            lat, lon, height = map(float, rest[:3])
            quality = int(rest[3]) if len(rest) > 3 else 0
            ns = int(rest[4]) if len(rest) > 4 else 0
            sdn = float(rest[5]) if len(rest) > 5 else math.nan
            sde = float(rest[6]) if len(rest) > 6 else math.nan
            sdu = float(rest[7]) if len(rest) > 7 else math.nan
        except (ValueError, IndexError):
            continue
        rows.append(Position(stamp, lat, lon, height, quality, ns, sde, sdn, sdu))
    if not rows:
        raise ValueError(f"No position solutions could be parsed from {path}")
    rows.sort(key=lambda p: p.utc_unix)
    return rows


def write_positions(path: Path, positions: Iterable[Position]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["utc_iso", "utc_unix", "latitude_deg", "longitude_deg",
                         "ellipsoidal_height_m", "quality", "satellites",
                         "sigma_e_m", "sigma_n_m", "sigma_u_m"])
        for p in positions:
            iso = datetime.fromtimestamp(p.utc_unix, timezone.utc).isoformat()
            writer.writerow([iso, f"{p.utc_unix:.6f}", f"{p.latitude_deg:.10f}",
                             f"{p.longitude_deg:.10f}", f"{p.height_m:.4f}", p.quality,
                             p.satellites, p.sigma_e_m, p.sigma_n_m, p.sigma_u_m])


def command_solve(args: argparse.Namespace) -> int:
    convbin = shutil.which(args.convbin)
    rnx2rtkp = shutil.which(args.rnx2rtkp)
    if not convbin or not rnx2rtkp:
        missing = [name for name, found in ((args.convbin, convbin), (args.rnx2rtkp, rnx2rtkp)) if not found]
        raise RuntimeError("RTKLIB executable(s) not found: " + ", ".join(missing))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fmcw_rtklib_") as tmp:
        work = Path(tmp)
        rover = materialize_rtcm(args.rover_rtcm, work, "rover")
        base = materialize_rtcm(args.base_rtcm, work, "base")
        rover_obs, rover_nav = convert_rtcm(rover, work / "rover", convbin)
        base_obs, base_nav = convert_rtcm(base, work / "base", convbin)
        config = work / "rtklib.conf"
        raw_pos = work / "solution.pos"
        write_rtklib_config(config)
        run_checked([rnx2rtkp, "-k", config, "-o", raw_pos,
                     rover_obs, base_obs, *rover_nav, *base_nav])
        positions = parse_rtklib_pos(raw_pos)
        write_positions(args.output, positions)
    print(f"Wrote {len(positions)} timestamped locations to {args.output}")
    return 0


def read_positions(path: Path) -> list[Position]:
    rows: list[Position] = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(Position(
                float(row["utc_unix"]), float(row["latitude_deg"]),
                float(row["longitude_deg"]), float(row["ellipsoidal_height_m"]),
                int(row.get("quality", 0) or 0), int(row.get("satellites", 0) or 0)))
    if not rows:
        raise ValueError(f"No locations in {path}")
    return sorted(rows, key=lambda p: p.utc_unix)


def csv_edges(scan: Scan) -> tuple[list[int], list[float]]:
    samples: list[int] = []
    times: list[float] = []
    if not scan.edge_path:
        return samples, times
    with scan.edge_path.open(newline="") as f:
        for row in csv.DictReader(f):
            try:
                samples.append(int(row["audio_sample"]))
                times.append(float(row["utc_unix_estimated"]))
            except (KeyError, TypeError, ValueError):
                continue
    return samples, times


def pcm_sample(fmt: str, raw: bytes, offset: int) -> float:
    if fmt == "b":
        return (raw[offset] - 128) / 128.0
    if fmt == "h":
        return struct.unpack_from("<h", raw, offset)[0] / 32768.0
    if fmt == "i24":
        value = int.from_bytes(raw[offset:offset + 3], "little", signed=True)
        return value / 8388608.0
    return struct.unpack_from("<i", raw, offset)[0] / 2147483648.0


def detect_prf_edges(path: Path, channel: int, threshold: float,
                     min_gap_s: float) -> tuple[list[int], int]:
    """Streaming rising-edge detector for integer PCM WAV files."""
    edges: list[int] = []
    with wave.open(str(path), "rb") as wav:
        channels, width, fs = wav.getnchannels(), wav.getsampwidth(), wav.getframerate()
        if channel < 0 or channel >= channels:
            raise ValueError(f"PRF channel {channel} is outside {path.name}'s {channels} channels")
        if width not in (1, 2, 3, 4):
            raise ValueError(f"Unsupported PCM sample width: {width}")
        fmt = {1: "b", 2: "h", 3: "i24", 4: "i"}[width]
        frame_bytes = channels * width
        frame_index = 0
        previous_high = False
        last_edge = -10**18
        min_gap = round(min_gap_s * fs)
        while True:
            raw = wav.readframes(65536)
            if not raw:
                break
            frames = len(raw) // frame_bytes
            for i in range(frames):
                offset = i * frame_bytes + channel * width
                high = pcm_sample(fmt, raw, offset) > threshold
                absolute = frame_index + i
                if high and not previous_high and absolute - last_edge >= min_gap:
                    edges.append(absolute)
                    last_edge = absolute
                previous_high = high
            frame_index += frames
    return edges, fs


def pulse_timing(scan: Scan, prf_channel: int | None, threshold: float,
                 min_gap_s: float) -> tuple[list[int], list[float], int]:
    samples, times = csv_edges(scan)
    channels, _, fs, _ = wav_parameters(scan.wav)
    if samples:
        return samples, times, fs
    channel_was_explicit = prf_channel is not None
    if prf_channel is None:
        prf_channel = int(scan.metadata.get("combined_edge_channel",
                                           scan.metadata.get("edge_channel", "0")))
    samples, fs = detect_prf_edges(scan.wav, prf_channel, threshold, min_gap_s)
    # Some recordings have stale device/channel metadata. When the configured
    # channel is silent, find the active pulse train, while preserving an
    # explicit user override exactly.
    if not samples and not channel_was_explicit:
        candidates: list[tuple[int, int, list[int]]] = []
        for channel in range(channels):
            if channel == prf_channel:
                continue
            detected, _ = detect_prf_edges(scan.wav, channel, threshold, min_gap_s)
            candidates.append((len(detected), channel, detected))
        count, detected_channel, detected = max(candidates, default=(0, -1, []))
        if count:
            samples = detected
            print(f"{scan.wav.name}: metadata PRF channel {prf_channel} was silent; "
                  f"using detected channel {detected_channel} ({count} edges)")
    start = scan.start.timestamp()
    times = [start + sample / fs for sample in samples]
    return samples, times, fs


def require_scientific_stack():
    try:
        import numpy as np
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError("Processing requires numpy and soundfile; install requirements.txt") from exc
    sys.path.insert(0, str(REPO_ROOT))
    import Imaging
    return np, sf, Imaging


def ecef(lat_deg: float, lon_deg: float, height: float) -> tuple[float, float, float]:
    a = 6378137.0
    e2 = 6.69437999014e-3
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    n = a / math.sqrt(1.0 - e2 * math.sin(lat) ** 2)
    return ((n + height) * math.cos(lat) * math.cos(lon),
            (n + height) * math.cos(lat) * math.sin(lon),
            (n * (1.0 - e2) + height) * math.sin(lat))


def positions_enu(np, positions: list[Position], pulse_times: list[float],
                  radar_height_m: float):
    t = np.asarray([p.utc_unix for p in positions])
    if pulse_times[0] < t[0] or pulse_times[-1] > t[-1]:
        raise ValueError(
            "GNSS trajectory does not cover pulse times: "
            f"GNSS {datetime.fromtimestamp(t[0], timezone.utc).isoformat()} .. "
            f"{datetime.fromtimestamp(t[-1], timezone.utc).isoformat()}, "
            f"pulses {datetime.fromtimestamp(pulse_times[0], timezone.utc).isoformat()} .. "
            f"{datetime.fromtimestamp(pulse_times[-1], timezone.utc).isoformat()}")
    xyz = np.asarray([ecef(p.latitude_deg, p.longitude_deg, p.height_m) for p in positions])
    pt = np.asarray(pulse_times)
    interp = np.column_stack([np.interp(pt, t, xyz[:, axis]) for axis in range(3)])
    lat0 = math.radians(positions[0].latitude_deg)
    lon0 = math.radians(positions[0].longitude_deg)
    rotation = np.asarray([
        [-math.sin(lon0), math.cos(lon0), 0.0],
        [-math.sin(lat0) * math.cos(lon0), -math.sin(lat0) * math.sin(lon0), math.cos(lat0)],
        [math.cos(lat0) * math.cos(lon0), math.cos(lat0) * math.sin(lon0), math.sin(lat0)],
    ])
    enu = (interp - interp[0]) @ rotation.T
    # GNSS gives relative vertical motion; this offset defines the target plane.
    enu[:, 2] += radar_height_m
    return enu


def range_profiles(np, sf, scan: Scan, edge_samples: list[int], radar_channel: int,
                   pulse_seconds: float, fstart: float, fstop: float,
                   oversample: int):
    audio, fs = sf.read(scan.wav, always_2d=True)
    if radar_channel < 0 or radar_channel >= audio.shape[1]:
        raise ValueError(f"Radar channel {radar_channel} is outside {audio.shape[1]} channels")
    count = round(pulse_seconds * fs)
    valid = [sample for sample in edge_samples if sample + count <= audio.shape[0]]
    if not valid:
        raise ValueError(f"No complete radar pulses found in {scan.wav.name}")
    pulses = np.vstack([audio[s:s + count, radar_channel] for s in valid])
    pulses -= pulses.mean(axis=1, keepdims=True)
    pulses -= pulses.mean(axis=0, keepdims=True)
    nfft = max(4, oversample) * count
    profiles = np.fft.ifft(pulses * np.hanning(count)[None, :], n=nfft, axis=1)
    dr = 299792458.0 / (2.0 * (fstop - fstart)) * count / nfft
    if len(valid) > 2:
        profiles *= np.hanning(len(valid))[:, None]
    return profiles, dr, len(valid)


def save_pulse_csv(path: Path, samples: list[int], times: list[float], positions) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pulse_index", "audio_sample", "utc_iso", "utc_unix",
                         "east_m", "north_m", "up_m"])
        for i, (sample, stamp, pos) in enumerate(zip(samples, times, positions)):
            writer.writerow([i, sample, datetime.fromtimestamp(stamp, timezone.utc).isoformat(),
                             f"{stamp:.9f}", *[f"{v:.6f}" for v in pos]])


def process_one_scan(args: argparse.Namespace, scan: Scan, locations: list[Position]) -> Path:
    np, sf, Imaging = require_scientific_stack()
    edge_samples, pulse_times, _ = pulse_timing(
        scan, args.prf_channel, args.prf_threshold, args.min_prf_gap)
    if not edge_samples:
        raise ValueError(f"No PRF rising edges found for {scan.wav.name}")
    profiles, dr, used = range_profiles(np, sf, scan, edge_samples, args.radar_channel,
                                        args.pulse_seconds, args.fstart, args.fstop,
                                        args.oversample)
    edge_samples, pulse_times = edge_samples[:used], pulse_times[:used]
    antenna = positions_enu(np, locations, pulse_times, args.radar_height_m)
    x0, x1 = float(antenna[:, 0].min()), float(antenna[:, 0].max())
    y0, y1 = float(antenna[:, 1].min()), float(antenna[:, 1].max())
    cross = (x0 - args.image_margin_m, x1 + args.image_margin_m)
    down = (y0 - args.image_margin_m, y1 + args.image_margin_m)
    image, x_axis, y_axis, _ = Imaging.backproject(
        antenna, profiles, dr, crossrange=cross, downrange=down,
        resolution=(args.image_pixels, args.image_pixels), fstart=args.fstart,
        fstop=args.fstop, phase_sign=args.phase_sign, output_db=True,
        normalize_db=True, flip_lr=False, flip_ud=False, transpose_output=False)
    args.output.mkdir(parents=True, exist_ok=True)
    stem = scan.wav.stem
    np.savez_compressed(args.output / f"{stem}_backprojection.npz", image_db=image,
                        crossrange_m=x_axis, downrange_m=y_axis, antenna_enu_m=antenna,
                        pulse_utc_unix=np.asarray(pulse_times), range_bin_m=dr)
    save_pulse_csv(args.output / f"{stem}_pulse_locations.csv",
                   edge_samples, pulse_times, antenna)
    if not args.no_png:
        import matplotlib.pyplot as plt
        peak = float(np.max(image))
        fig, ax = plt.subplots(figsize=(7, 6))
        plot = ax.imshow(image, origin="lower", cmap="turbo",
                         extent=(x_axis[0], x_axis[-1], y_axis[0], y_axis[-1]),
                         vmin=peak - args.dynamic_range_db, vmax=peak, aspect="equal")
        fig.colorbar(plot, ax=ax, label="Normalized magnitude (dB)")
        ax.set(xlabel="East / cross-range (m)", ylabel="North / down-range (m)",
               title=stem)
        fig.tight_layout()
        fig.savefig(args.output / f"{stem}_backprojection.png", dpi=180)
        plt.close(fig)
    return args.output / f"{stem}_backprojection.npz"


def command_process(args: argparse.Namespace) -> int:
    locations = read_positions(args.locations)
    scans = discover_scans(args.scans)
    if args.wav:
        requested = Path(args.wav).resolve()
        scans = [scan for scan in scans if scan.wav.resolve() == requested]
    if not scans:
        raise ValueError("No matching WAV scans found")
    failures = 0
    for scan in scans:
        try:
            output = process_one_scan(args, scan, locations)
            print(f"Wrote {output}")
        except Exception as exc:
            failures += 1
            print(f"SKIP {scan.wav.name}: {exc}", file=sys.stderr)
            if args.fail_fast:
                raise
    if failures == len(scans):
        raise RuntimeError("No scans were processed successfully")
    return 1 if failures else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("inventory", help="show scans and available RTCM3 streams")
    inv.add_argument("--scans", type=Path, default=DEFAULT_SCANS)
    inv.add_argument("--base", type=Path, default=DEFAULT_BASE)
    inv.add_argument("--rover", type=Path, default=DEFAULT_ROVER)
    inv.set_defaults(func=command_inventory)

    solve = sub.add_parser("solve-rtcm", help="PPK-solve one rover/base RTCM3 pair")
    solve.add_argument("--rover-rtcm", required=True,
                       help="RTCM3 file, ZIP, or 'archive.zip!member.rtcm3'")
    solve.add_argument("--base-rtcm", required=True,
                       help="RTCM3 file, ZIP, or 'archive.zip!member.rtcm3'")
    solve.add_argument("--output", type=Path, default=HERE / "timestamped_locations.csv")
    solve.add_argument("--convbin", default="convbin")
    solve.add_argument("--rnx2rtkp", default="rnx2rtkp")
    solve.set_defaults(func=command_solve)

    proc = sub.add_parser("process-scans", help="align scans to GNSS and backproject")
    proc.add_argument("--locations", type=Path, default=HERE / "timestamped_locations.csv")
    proc.add_argument("--scans", type=Path, default=DEFAULT_SCANS)
    proc.add_argument("--wav", help="process only this WAV")
    proc.add_argument("--output", type=Path, default=HERE / "Output")
    proc.add_argument("--radar-channel", type=int, default=1, help="zero-based WAV channel")
    proc.add_argument("--prf-channel", type=int, help="zero-based; metadata default if omitted")
    proc.add_argument("--prf-threshold", type=float, default=0.2)
    proc.add_argument("--min-prf-gap", type=float, default=0.025)
    proc.add_argument("--pulse-seconds", type=float, default=0.005)
    proc.add_argument("--fstart", type=float, default=2280e6)
    proc.add_argument("--fstop", type=float, default=2580e6)
    proc.add_argument("--radar-height-m", type=float, default=6.0 * 0.3048)
    proc.add_argument("--oversample", type=int, default=8)
    proc.add_argument("--image-pixels", type=int, default=100)
    proc.add_argument("--image-margin-m", type=float, default=6.0)
    proc.add_argument("--dynamic-range-db", type=float, default=15.0)
    proc.add_argument("--phase-sign", type=float, default=1.0)
    proc.add_argument("--no-png", action="store_true")
    proc.add_argument("--fail-fast", action="store_true")
    proc.set_defaults(func=command_process)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
