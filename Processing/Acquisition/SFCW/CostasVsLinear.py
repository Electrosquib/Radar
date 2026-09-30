"""A/B test Costas versus linear stepping on an uncalibrated moving fan."""
import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
from SFCW import SFCWRadar


def use_order(order, freqs, rx_profiles, tx_profiles):
    radar.FREQS = freqs[order]
    radar.fastlock_profiles = rx_profiles[order]
    radar.tx_fastlock_profiles = tx_profiles[order]


def capture(order):
    t0 = time.perf_counter()
    radar.sweep()
    elapsed = time.perf_counter() - t0
    acquired = radar.S.copy().reshape(len(order), radar.num_freqs)
    sorted_response = np.empty_like(acquired)
    sorted_response[order] = acquired
    spectrum = sorted_response.ravel()
    spectrum = (spectrum - spectrum.mean()) * np.hanning(spectrum.size)
    return np.fft.ifft(spectrum), elapsed


def metrics(profiles, times, target, guard=5):
    dynamic = np.abs(profiles - profiles.mean(axis=0))
    n = dynamic.shape[1]
    near = np.arange(max(1, target - 2), min(n // 2, target + 3))
    far = np.ones(n // 2, bool)
    far[max(0, target - guard):target + guard + 1] = False
    peaks = dynamic[:, near].max(axis=1)
    bins = near[np.argmax(dynamic[:, near], axis=1)]
    floor = np.median(dynamic[:, :n // 2][:, far], axis=1)
    contrast = 20 * np.log10((peaks + 1e-12) / (floor + 1e-12))
    return dynamic, contrast, bins, np.asarray(times)


def stat(name, values, unit):
    return f"{name:18s} {values.mean():9.3f} +/- {values.std(ddof=1):7.3f} {unit}"


def main():
    global radar
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--trials", type=int, default=12)
    args = parser.parse_args()
    if args.trials < 3:
        raise ValueError("Use at least 3 trials for a meaningful standard deviation")
    radar = SFCWRadar(
        verbose=False,
        Fmin=3e9,
        Fmax=3.6e9,
        Fs=20e6,
        use_ps_controller=False,
    )
    radar.verbose = False
    costas = np.asarray(radar.step_order, int)
    undo = np.argsort(costas)
    freqs = np.asarray(radar.FREQS)[undo]
    rx_profiles = np.asarray(radar.fastlock_profiles)[undo]
    tx_profiles = np.asarray(radar.tx_fastlock_profiles)[undo]
    orders = {"Costas": costas, "Linear": np.arange(len(costas))}
    profiles, times = {k: [] for k in orders}, {k: [] for k in orders}
    input("Point at the running fan, keep everything still, then press Enter...")
    try:
        for trial in range(args.trials):
            sequence = ["Costas", "Linear"] if trial % 2 == 0 else ["Linear", "Costas"]
            for name in sequence:
                use_order(orders[name], freqs, rx_profiles, tx_profiles)
                profile, elapsed = capture(orders[name])
                profiles[name].append(profile); times[name].append(elapsed)
            print(f"Captured pair {trial + 1}/{args.trials}")
        profiles = {k: np.asarray(v) for k, v in profiles.items()}
        motion = sum(np.mean(np.abs(v - v.mean(axis=0)) ** 2, axis=0) for v in profiles.values())
        target = 2 + int(np.argmax(motion[2:motion.size // 2]))
        results = {k: metrics(profiles[k], times[k], target) for k in orders}
        print(f"\nAuto-selected moving target bin: {target} (range intentionally uncalibrated)")
        for name, (_, contrast, bins, secs) in results.items():
            print(f"\n{name}")
            print(stat("contrast", contrast, "dB")); print(stat("peak bin", bins, "bins"))
            print(stat("sweep time", secs, "s"))
        c, l = results["Costas"], results["Linear"]
        print("\n" + stat("paired gain", c[1] - l[1], "dB"))
        print(f"Costas jitter change: {(c[2].std(ddof=1)/(l[2].std(ddof=1)+1e-12)-1)*100:+.1f}%")
        fig, ax = plt.subplots(2, 2, figsize=(12, 8))
        for name, (dyn, _, _, _) in results.items():
            mean, std = dyn.mean(axis=0), dyn.std(axis=0, ddof=1)
            x = np.arange(mean.size // 2); y = 20*np.log10(mean[:x.size]+1e-12)
            ax[0, 0].plot(x, y, label=name)
            ax[0, 0].fill_between(x, 20*np.log10(np.maximum(mean[:x.size]-std[:x.size], 1e-12)), 20*np.log10(mean[:x.size]+std[:x.size]+1e-12), alpha=.15)
        ax[0, 0].axvline(target, color="k", ls="--"); ax[0, 0].set(xlabel="Uncalibrated range bin", ylabel="Dynamic magnitude (dB)"); ax[0, 0].legend()
        ax[0, 1].boxplot([c[1], l[1]], tick_labels=["Costas", "Linear"]); ax[0, 1].set_ylabel("Target/background contrast (dB)")
        ax[1, 0].boxplot([c[2], l[2]], tick_labels=["Costas", "Linear"]); ax[1, 0].set_ylabel("Peak bin")
        ax[1, 1].boxplot([c[3], l[3]], tick_labels=["Costas", "Linear"]); ax[1, 1].set_ylabel("Sweep time (s)")
        fig.suptitle(f"Costas vs linear, {args.trials} paired trials"); fig.tight_layout(); plt.show()
    finally:
        radar.close()


if __name__ == "__main__": main()
