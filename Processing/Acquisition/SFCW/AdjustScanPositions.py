#!/usr/bin/env python3
"""Adjust the rail positions of an existing SFCW SAR scan.

The acquisition code saves positions in both ``metadata.json`` and
``range_profiles.npz``.  This helper updates both files so regenerated SAR
images use the corrected aperture spacing.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


INCHES_PER_METER = 1.0 / 0.0254


def resolve_scene_paths(path: Path) -> tuple[Path, Path]:
    """Return the metadata and range-profile paths for a scene path."""
    path = path.expanduser().resolve()
    if path.is_dir():
        return path / "metadata.json", path / "range_profiles.npz"
    if path.name == "metadata.json" or path.suffix.lower() == ".json":
        return path, path.with_name("range_profiles.npz")
    raise ValueError("SCENE must be a scene directory or a metadata JSON file")


def load_metadata(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Metadata file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    scans = metadata.get("scans")
    if not isinstance(scans, list) or not scans:
        raise ValueError(f"No scans found in {path}")
    return metadata


def positions_in_inches(metadata: dict) -> np.ndarray:
    """Read scan positions, accepting either of the metadata position fields."""
    positions = []
    for list_index, scan in enumerate(metadata["scans"]):
        try:
            if "position_inches" in scan:
                position = float(scan["position_inches"])
            else:
                position = float(scan["position_meters"]) * INCHES_PER_METER
        except (KeyError, TypeError, ValueError) as exc:
            scan_index = scan.get("scan_index", list_index)
            raise ValueError(
                f"Scan {scan_index} has no valid position_inches or "
                "position_meters value"
            ) from exc
        if not np.isfinite(position):
            raise ValueError(f"Scan {list_index} has a non-finite position")
        positions.append(position)
    return np.asarray(positions, dtype=float)


def evenly_spaced_positions(
    current_inches: np.ndarray,
    spacing_inches: float,
    start_inches: float | None = None,
    direction: str = "preserve",
) -> np.ndarray:
    """Build evenly spaced positions while optionally preserving travel direction."""
    if current_inches.ndim != 1 or not len(current_inches):
        raise ValueError("At least one current position is required")
    if not np.isfinite(spacing_inches) or spacing_inches <= 0:
        raise ValueError("Spacing must be a finite number greater than zero")
    if start_inches is None:
        start_inches = float(current_inches[0])
    if not np.isfinite(start_inches):
        raise ValueError("Start position must be finite")

    if direction == "preserve":
        finite_deltas = np.diff(current_inches)
        finite_deltas = finite_deltas[np.isfinite(finite_deltas)]
        sign = -1.0 if len(finite_deltas) and np.median(finite_deltas) < 0 else 1.0
    elif direction == "decreasing":
        sign = -1.0
    elif direction == "increasing":
        sign = 1.0
    else:
        raise ValueError(f"Unknown direction: {direction}")

    return start_inches + sign * spacing_inches * np.arange(len(current_inches))


def update_metadata_positions(metadata: dict, positions_inches: np.ndarray) -> None:
    if len(metadata["scans"]) != len(positions_inches):
        raise ValueError("Position count does not match metadata scan count")
    for scan, position in zip(metadata["scans"], positions_inches):
        position = float(position)
        scan["position_inches"] = position
        scan["position_meters"] = position * 0.0254


def load_npz_payload(path: Path, expected_count: int) -> dict[str, np.ndarray] | None:
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as archive:
        if "rail_pos_in" not in archive:
            raise ValueError(f"{path} does not contain rail_pos_in")
        if len(archive["rail_pos_in"]) != expected_count:
            raise ValueError(
                f"Metadata has {expected_count} scans, but {path} has "
                f"{len(archive['rail_pos_in'])} positions"
            )
        return {key: archive[key].copy() for key in archive.files}


def backup_file(path: Path, timestamp: str) -> Path:
    backup = path.with_name(f"{path.name}.{timestamp}.bak")
    shutil.copy2(path, backup)
    return backup


def save_changes(
    metadata_path: Path,
    metadata: dict,
    profiles_path: Path,
    npz_payload: dict[str, np.ndarray] | None,
    positions_inches: np.ndarray,
    make_backup: bool = True,
) -> list[Path]:
    """Validate first, then replace the metadata and optional NPZ files."""
    backups: list[Path] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if make_backup:
        backups.append(backup_file(metadata_path, timestamp))
        if npz_payload is not None:
            backups.append(backup_file(profiles_path, timestamp))

    metadata_tmp = metadata_path.with_name(f".{metadata_path.name}.tmp")
    profiles_tmp = profiles_path.with_name(f".{profiles_path.name}.tmp.npz")
    try:
        metadata_tmp.write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        if npz_payload is not None:
            npz_payload["rail_pos_in"] = positions_inches.astype(float)
            np.savez(profiles_tmp, **npz_payload)
            profiles_tmp.replace(profiles_path)
        metadata_tmp.replace(metadata_path)
    finally:
        metadata_tmp.unlink(missing_ok=True)
        profiles_tmp.unlink(missing_ok=True)
    return backups


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Set uniform scan spacing in an existing SFCW scene's metadata "
            "and range_profiles.npz file."
        )
    )
    parser.add_argument("scene", type=Path, metavar="SCENE")
    parser.add_argument(
        "--spacing", type=float, required=True,
        help="positive distance between adjacent scans",
    )
    parser.add_argument(
        "--start", type=float,
        help="first scan position (default: keep its current position)",
    )
    parser.add_argument(
        "--unit", choices=("in", "m"), default="in",
        help="unit for --spacing and --start (default: in)",
    )
    parser.add_argument(
        "--direction", choices=("preserve", "increasing", "decreasing"),
        default="preserve", help="position direction (default: preserve)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print the proposed changes without writing files",
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="do not create timestamped .bak copies",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        metadata_path, profiles_path = resolve_scene_paths(args.scene)
        metadata = load_metadata(metadata_path)
        current = positions_in_inches(metadata)
        unit_scale = INCHES_PER_METER if args.unit == "m" else 1.0
        updated = evenly_spaced_positions(
            current,
            spacing_inches=args.spacing * unit_scale,
            start_inches=None if args.start is None else args.start * unit_scale,
            direction=args.direction,
        )
        npz_payload = load_npz_payload(profiles_path, len(updated))
        update_metadata_positions(metadata, updated)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Scene: {metadata.get('scene_title', metadata_path.parent.name)}")
    print(f"Scans: {len(updated)}")
    print(
        f"Positions (in): {current[0]:.6g} .. {current[-1]:.6g} -> "
        f"{updated[0]:.6g} .. {updated[-1]:.6g}"
    )
    print(f"New spacing: {abs(updated[1] - updated[0]) if len(updated) > 1 else 0:.6g} in")
    if npz_payload is None:
        print(f"Note: {profiles_path.name} was not found; updating metadata only.")
    if args.dry_run:
        print("Dry run; no files changed.")
        return 0

    try:
        backups = save_changes(
            metadata_path, metadata, profiles_path, npz_payload, updated,
            make_backup=not args.no_backup,
        )
    except OSError as exc:
        print(f"error: could not save changes: {exc}", file=sys.stderr)
        return 2

    print(f"Updated {metadata_path}")
    if npz_payload is not None:
        print(f"Updated {profiles_path}")
    for backup in backups:
        print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
