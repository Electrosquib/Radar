"""Measure intra-sweep Doppler with paired up/down SFCW profiles.

Use one dominant moving reflector in the selected range gate. Positive velocity
means increasing range (receding). A large phase-fit RMS indicates clutter,
multiple targets, or Doppler aliasing.
"""

import argparse
import time

import numpy as np

from SFCW import SFCWRadar


def capture_timed_sweep(radar, reverse=False):
    """Capture one sweep while retaining each LO group's midpoint time."""
    count = len(radar.FREQS)
    responses = np.empty((count, radar.num_freqs), dtype=np.complex128)
    timestamps = np.empty(count)
    starts = list(range(0, count, 8))
    if reverse:
        starts.reverse()

    for start in starts:
        radar.load_fastlock(start)
        indices = list(range(start, min(start + 8, count)))
        if reverse:
            indices.reverse()
        for index in indices:
            radar.retune(radar.FREQS[index], index - start)
            time.sleep(radar.retune_delay)
            capture_start = time.perf_counter()
            responses[index] = radar.extract_bb_phasors()
            timestamps[index] = (capture_start + time.perf_counter()) / 2

    return responses, timestamps


def find_target_range(radar, responses, minimum, maximum):
    """Find the strongest range bin inside the requested range gate."""
    radar.S[:] = responses.reshape(-1)
    range_axis, profile = radar.get_range_profile(plot=False, cal=False)
    gate = (range_axis >= minimum) & (range_axis <= maximum)
    if not np.any(gate):
        raise ValueError("The requested range gate contains no profile bins")
    indices = np.flatnonzero(gate)
    return float(range_axis[indices[np.argmax(np.abs(profile[gate]))]])


def estimate_doppler(
    radar, up_response, up_time, down_response, down_time,
    target_range=None, range_min=0.25, range_max=10.0,
):
    """Cancel static frequency phase and fit motion phase versus f * delta-t."""
    if target_range is None:
        target_range = find_target_range(
            radar, up_response, range_min, range_max
        )

    frequencies = (
        np.asarray(radar.FREQS)[:, None] + radar.bb_freqs[None, :]
    )
    steering = np.exp(1j * 4 * np.pi * frequencies * target_range / radar.C)
    up_target = np.sum(up_response * steering, axis=1)
    down_target = np.sum(down_response * steering, axis=1)
    cross = down_target * np.conj(up_target)

    frequency = np.mean(frequencies, axis=1)
    x = frequency * (down_time - up_time)
    order = np.argsort(x)
    x = x[order]
    phase = np.unwrap(np.angle(cross[order]))
    weights = np.sqrt(np.abs(cross[order]))
    x_centered = x - np.average(x, weights=weights)
    slope, intercept = np.polyfit(x_centered, phase, 1, w=weights)
    fitted = slope * x_centered + intercept

    velocity = -radar.C * slope / (4 * np.pi)
    center_frequency = float(np.mean(frequencies))
    doppler = 2 * center_frequency * velocity / radar.C
    phase_rms = np.sqrt(np.average((phase - fitted) ** 2, weights=weights))
    spacing = np.max(np.diff(x))
    velocity_limit = np.inf if spacing <= 0 else radar.C / (4 * spacing)
    return target_range, doppler, velocity, np.degrees(phase_rms), velocity_limit


def parse_args():
    parser = argparse.ArgumentParser(
        description="Measure intra-sweep Doppler using alternating SFCW sweeps"
    )
    parser.add_argument("--device", default="usb:")
    parser.add_argument("--fmin", type=float, default=3e9)
    parser.add_argument("--fmax", type=float, default=4e9)
    parser.add_argument("--fs", type=float, default=20e6)
    parser.add_argument("--rx-port", type=int, default=1)
    parser.add_argument("--rx-loopback-port", type=int, default=0)
    parser.add_argument("--tx-port", type=int, default=0)
    parser.add_argument("--tx-loopback-port", type=int, default=1)
    parser.add_argument("--captures", type=int, default=1)
    parser.add_argument("--measurements", type=int, default=0,
                        help="up/down pairs to capture; 0 runs until Ctrl+C")
    parser.add_argument("--target-range", type=float,
                        help="known target range in meters; otherwise auto-detect")
    parser.add_argument("--range-min", type=float, default=0.25)
    parser.add_argument("--range-max", type=float, default=10.0)
    parser.add_argument("--retune-delay", type=float, default=100e-6)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.captures < 1:
        raise ValueError("--captures must be at least 1")
    radar = SFCWRadar(
        device_string=args.device,
        Fmin=args.fmin,
        Fmax=args.fmax,
        Fs=args.fs,
        verbose=args.verbose,
        rx_port=args.rx_port,
        rx_loopback_port=args.rx_loopback_port,
        tx_port=args.tx_port,
        tx_loopback_port=args.tx_loopback_port,
        use_ps_controller=False,
    )
    radar.CAPTURE_AVERAGES = args.captures
    radar.retune_delay = args.retune_delay

    print("Place one dominant moving reflector in the range gate.")
    print("Positive velocity means increasing range. Press Ctrl+C to stop.")
    measurement = 0
    try:
        while args.measurements == 0 or measurement < args.measurements:
            pair_start = time.perf_counter()
            up_response, up_time = capture_timed_sweep(radar)
            down_response, down_time = capture_timed_sweep(radar, reverse=True)
            result = estimate_doppler(
                radar, up_response, up_time, down_response, down_time,
                args.target_range, args.range_min, args.range_max,
            )
            target_range, doppler, velocity, phase_rms, velocity_limit = result
            measurement += 1
            print(
                f"{measurement:04d}  range={target_range:7.3f} m  "
                f"doppler={doppler:+9.3f} Hz  velocity={velocity:+8.4f} m/s  "
                f"fit_rms={phase_rms:6.1f} deg  "
                f"alias_limit~+/-{velocity_limit:.3f} m/s  "
                f"pair_time={time.perf_counter() - pair_start:.3f} s"
            )
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        radar.close()


if __name__ == "__main__":
    main()
