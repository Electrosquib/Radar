#!/usr/bin/env python3
"""Capture one AD9361 RX buffer per frequency using rolling fastlock slots.

The AD9361 contains eight RX fastlock profile slots.  This script first tunes
and calibrates every requested frequency, saves every resulting 16-byte
profile in host memory, loads the first eight into the transceiver, and then
uses the eight hardware slots as a ring.  After leaving a slot, the script
refills that now-inactive slot with the profile needed eight hops later.

Run ``python3 scripts/rolling_fastlock_rx.py --dry-run`` without hardware to
inspect and validate the rolling schedule.
"""

from __future__ import annotations

import argparse
import csv
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


# ---------------------------------------------------------------------------
# User configuration
# ---------------------------------------------------------------------------

SDR_URI = "ip:192.168.2.1"

# Edit this list/comprehension to specify the sweep frequencies in hertz.
# Starting at 70 MHz, exact 20 MHz increments end at 5.990 GHz; 6.000 GHz is
# not on that grid.  The explicit final entry covers 6 GHz with one last 10 MHz
# step.  Remove it for a strict 20 MHz grid, or start at 80 MHz if every step
# must be 20 MHz and the final point must be exactly 6 GHz.
FREQUENCIES_HZ = [
    *range(300_000_000, 600_000_000, 20_000_000),]

SAMPLE_RATE_HZ = 30_720_000
RF_BANDWIDTH_HZ = 20_000_000
RX_BUFFER_SAMPLES = 32_768
RX_CHANNELS = [0]

GAIN_CONTROL_MODE = "slow_attack"  # "slow_attack", "fast_attack", or "manual"
MANUAL_RX_GAIN_DB = 30

# ADI quotes roughly 15-25 us for a fastlock hop.  Fifty microseconds provides
# margin before starting the next DMA capture.  Host/OS scheduling may make the
# actual delay longer; Python is not a deterministic microsecond scheduler.
HOP_SETTLE_SECONDS = 50e-6

OUTPUT_DIRECTORY = Path("fastlock_captures")
SAVE_CAPTURES = True

FASTLOCK_SLOT_COUNT = 8
FASTLOCK_PROFILE_WORDS = 16
AD9361_MIN_RX_HZ = 70_000_000
AD9361_MAX_RX_HZ = 6_000_000_000


@dataclass(frozen=True)
class FastlockProfile:
    frequency_hz: int
    words: tuple[int, ...]

    def payload_for_slot(self, slot: int) -> str:
        """Return the IIO fastlock_load format: ``slot word0,...,word15``."""
        return f"{slot} " + ",".join(str(word) for word in self.words)


def validate_frequencies(frequencies: Sequence[int]) -> None:
    if not frequencies:
        raise ValueError("FREQUENCIES_HZ must contain at least one frequency")
    if any(not isinstance(freq, int) for freq in frequencies):
        raise TypeError("Every frequency must be an integer number of hertz")
    if any(
        freq < AD9361_MIN_RX_HZ or freq > AD9361_MAX_RX_HZ
        for freq in frequencies
    ):
        raise ValueError(
            "RX frequencies must be between 70 MHz and 6 GHz inclusive"
        )


def parse_saved_profile(raw: str, expected_slot: int, frequency_hz: int) -> FastlockProfile:
    """Parse the value read from the RX_LO fastlock_save IIO attribute."""
    fields = raw.strip().split(None, 1)
    if len(fields) != 2:
        raise RuntimeError(f"Malformed fastlock_save value: {raw!r}")

    returned_slot = int(fields[0])
    words = tuple(int(value) for value in fields[1].split(","))
    if returned_slot != expected_slot:
        raise RuntimeError(
            f"Requested fastlock slot {expected_slot}, got slot {returned_slot}"
        )
    if len(words) != FASTLOCK_PROFILE_WORDS or any(
        word < 0 or word > 255 for word in words
    ):
        raise RuntimeError(
            f"Expected {FASTLOCK_PROFILE_WORDS} profile bytes, got {words!r}"
        )
    return FastlockProfile(frequency_hz, words)


def get_rx_lo_channel(sdr: Any) -> Any:
    channel = sdr._ctrl.find_channel("altvoltage0", True)
    if channel is None:
        raise RuntimeError("ad9361-phy RX_LO channel altvoltage0 was not found")

    required = {
        "frequency",
        "fastlock_store",
        "fastlock_save",
        "fastlock_load",
        "fastlock_recall",
    }
    missing = required.difference(channel.attrs)
    if missing:
        raise RuntimeError(
            "The board firmware lacks required RX fastlock attributes: "
            + ", ".join(sorted(missing))
        )
    return channel


def configure_receiver(sdr: Any) -> None:
    sdr.rx_enabled_channels = RX_CHANNELS
    sdr.sample_rate = SAMPLE_RATE_HZ
    sdr.rx_rf_bandwidth = RF_BANDWIDTH_HZ
    sdr.rx_buffer_size = RX_BUFFER_SAMPLES
    sdr.gain_control_mode_chan0 = GAIN_CONTROL_MODE
    if GAIN_CONTROL_MODE == "manual":
        sdr.rx_hardwaregain_chan0 = MANUAL_RX_GAIN_DB


def create_profiles(rx_lo: Any, frequencies: Sequence[int]) -> list[FastlockProfile]:
    """Normally tune each frequency and copy its calibration off-chip."""
    profiles: list[FastlockProfile] = []
    total = len(frequencies)

    print(f"Calibrating and saving {total} RX fastlock profiles...")
    for index, frequency_hz in enumerate(frequencies):
        slot = index % FASTLOCK_SLOT_COUNT

        # A normal frequency write performs the synth calibration.
        rx_lo.attrs["frequency"].value = str(frequency_hz)
        # Copy the current synthesizer settings into one of the eight slots.
        rx_lo.attrs["fastlock_store"].value = str(slot)
        # Select that slot for readback, then copy its 16 bytes to host RAM.
        rx_lo.attrs["fastlock_save"].value = str(slot)
        raw_profile = rx_lo.attrs["fastlock_save"].value
        profiles.append(parse_saved_profile(raw_profile, slot, frequency_hz))

        if index == 0 or (index + 1) % 25 == 0 or index + 1 == total:
            print(
                f"  {index + 1:4d}/{total}: "
                f"{frequency_hz / 1e6:9.3f} MHz"
            )

    return profiles


def preload_slots(rx_lo: Any, profiles: Sequence[FastlockProfile]) -> None:
    for slot, profile in enumerate(profiles[:FASTLOCK_SLOT_COUNT]):
        rx_lo.attrs["fastlock_load"].value = profile.payload_for_slot(slot)


def refill_departed_slot(
    rx_lo: Any,
    profiles: Sequence[FastlockProfile],
    departed_index: int,
) -> int | None:
    """Load the profile eight positions ahead into the slot just left."""
    refill_index = departed_index + FASTLOCK_SLOT_COUNT
    if refill_index >= len(profiles):
        return None

    slot = departed_index % FASTLOCK_SLOT_COUNT
    rx_lo.attrs["fastlock_load"].value = profiles[refill_index].payload_for_slot(slot)
    return refill_index


def write_capture(
    samples: Any,
    index: int,
    frequency_hz: int,
    output_directory: Path,
) -> Path:
    import numpy as np

    output_directory.mkdir(parents=True, exist_ok=True)
    path = output_directory / f"{index:04d}_{frequency_hz:010d}Hz.npy"
    np.save(path, samples)
    return path


def append_manifest(
    writer: csv.writer,
    index: int,
    frequency_hz: int,
    slot: int,
    capture_path: Path | None,
    recall_seconds: float,
    capture_seconds: float,
    refill_index: int | None,
) -> None:
    writer.writerow(
        [
            index,
            frequency_hz,
            slot,
            "" if capture_path is None else str(capture_path),
            f"{recall_seconds:.9f}",
            f"{capture_seconds:.9f}",
            "" if refill_index is None else refill_index,
        ]
    )


def capture_sweep(
    sdr: Any,
    rx_lo: Any,
    profiles: Sequence[FastlockProfile],
    output_directory: Path,
) -> None:
    """Recall, capture, advance, and refill the eight-slot rolling ring."""
    output_directory.mkdir(parents=True, exist_ok=True)
    manifest_path = output_directory / "manifest.csv"

    # Prime slot zero.  Each iteration ends by recalling the next frequency
    # before overwriting the slot that was just left.
    recall_started = time.perf_counter()
    rx_lo.attrs["fastlock_recall"].value = "0"
    recall_seconds = time.perf_counter() - recall_started
    time.sleep(HOP_SETTLE_SECONDS)

    with manifest_path.open("w", newline="", encoding="utf-8") as manifest:
        writer = csv.writer(manifest)
        writer.writerow(
            [
                "index",
                "frequency_hz",
                "fastlock_slot",
                "capture_file",
                "recall_command_seconds",
                "capture_seconds",
                "refill_profile_index",
            ]
        )

        for index, profile in enumerate(profiles):
            slot = index % FASTLOCK_SLOT_COUNT

            capture_started = time.perf_counter()
            samples = sdr.rx()
            capture_seconds = time.perf_counter() - capture_started

            capture_path = None
            if SAVE_CAPTURES:
                capture_path = write_capture(
                    samples, index, profile.frequency_hz, output_directory
                )

            next_recall_seconds = 0.0
            if index + 1 < len(profiles):
                next_slot = (index + 1) % FASTLOCK_SLOT_COUNT
                recall_started = time.perf_counter()
                rx_lo.attrs["fastlock_recall"].value = str(next_slot)
                next_recall_seconds = time.perf_counter() - recall_started

            # The synthesizer is now using the next slot, so the slot just
            # consumed is inactive and safe to overwrite.
            refill_index = refill_departed_slot(rx_lo, profiles, index)

            append_manifest(
                writer,
                index,
                profile.frequency_hz,
                slot,
                capture_path,
                recall_seconds,
                capture_seconds,
                refill_index,
            )
            manifest.flush()

            print(
                f"{index + 1:4d}/{len(profiles)}  "
                f"{profile.frequency_hz / 1e6:9.3f} MHz  "
                f"slot {slot}  capture {capture_seconds * 1e3:8.3f} ms"
            )

            recall_seconds = next_recall_seconds
            if index + 1 < len(profiles):
                time.sleep(HOP_SETTLE_SECONDS)

    print(f"Capture manifest: {manifest_path}")


def print_dry_run(frequencies: Sequence[int]) -> None:
    """Validate slot ownership without requiring pyadi-iio or hardware."""
    slot_contents: list[int | None] = [None] * FASTLOCK_SLOT_COUNT
    for index in range(min(FASTLOCK_SLOT_COUNT, len(frequencies))):
        slot_contents[index] = index

    print(
        f"{len(frequencies)} frequencies: "
        f"{frequencies[0] / 1e6:.3f} to {frequencies[-1] / 1e6:.3f} MHz"
    )
    print("index, frequency_MHz, recalled_slot, refill_profile_index")

    for index, frequency_hz in enumerate(frequencies):
        slot = index % FASTLOCK_SLOT_COUNT
        if slot_contents[slot] != index:
            raise RuntimeError(
                f"Slot {slot} contains profile {slot_contents[slot]}, expected {index}"
            )
        refill_index = index + FASTLOCK_SLOT_COUNT
        refill_text = ""
        if refill_index < len(frequencies):
            slot_contents[slot] = refill_index
            refill_text = str(refill_index)
        print(f"{index}, {frequency_hz / 1e6:.3f}, {slot}, {refill_text}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--uri",
        default=SDR_URI,
        help=f"IIO URI (default: {SDR_URI})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIRECTORY,
        help=f"capture directory (default: {OUTPUT_DIRECTORY})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print the rolling slot schedule without hardware",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_frequencies(FREQUENCIES_HZ)

    if args.dry_run:
        print_dry_run(FREQUENCIES_HZ)
        return 0

    try:
        import adi
    except ImportError as exc:
        raise SystemExit(
            "pyadi-iio is not installed. Install it with "
            "`python3 -m pip install pyadi-iio`."
        ) from exc

    print(f"Connecting to AD9361 at {args.uri}...")
    sdr = adi.ad9361(uri=args.uri)
    try:
        configure_receiver(sdr)
        rx_lo = get_rx_lo_channel(sdr)
        profiles = create_profiles(rx_lo, FREQUENCIES_HZ)
        preload_slots(rx_lo, profiles)
        capture_sweep(sdr, rx_lo, profiles, args.output)
    finally:
        if hasattr(sdr, "rx_destroy_buffer"):
            sdr.rx_destroy_buffer()
        if hasattr(sdr, "close"):
            sdr.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
