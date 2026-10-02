import numpy as np
import adi # type: ignore
import matplotlib.pyplot as plt # type: ignore
from datetime import datetime
import time
from collections import deque

class SFCWRadar:
    def __init__(self, 
            device_string="usb:", 
            Fmin=1000e6, 
            Fmax=1300e6, 
            Fs=20e6, 
            rx_port=1, 
            rx_loopback_port=0, 
            tx_port=0, 
            tx_loopback_port=1,

            verbose=True, 
            costas_mode=False,
            schroeder_phase=True
        ):
        self.RX_GAIN = 54
        self.LOOPBACK_GAIN = 0
        self.TX_GAIN = 0
        self.CAPTURE_AVERAGES = 4
        self.BUFF_SIZE = int(400 * self.CAPTURE_AVERAGES) # 20e6 / 1e6 = 20 samps. 8192 / 20 = 409.6. Must be an integer multiple to prevent spectral leakage
        self.BB_GAIN = 1
        self.SDR_BITS = 12
        self.C = 3e8
        self.TX_BB_SCALE = 2**14
        self.BB_SPACING = 2e6
        self.Fs = int(Fs)
        self.max_range = self.C / (2 * self.BB_SPACING)
        self.retune_delay = 100e-6

    
        self.verbose = True if verbose else False
        self.costas_mode = True if costas_mode else False
        self.schroeder_phase = True if schroeder_phase else False
        
        self.Fmin = Fmin
        self.Fmax = Fmax
        self.BW = Fmax - Fmin
        if self.BW <= 0:
            raise ValueError("Fmax must be greater than Fmin")

        self.FREQS = [int(i + self.Fs / 2) for i in np.arange(self.Fmin, self.Fmax, self.Fs)]
        self.fastlock_profiles = np.array([])
        self.tx_fastlock_profiles = np.array([])
        self.num_freqs = int(self.Fs // self.BB_SPACING)
        self.bb_freqs = np.arange(
            -self.Fs / 2,
            self.Fs / 2,
            self.BB_SPACING
        )
        if self.schroeder_phase:
            self.schroeder_phase_array = np.array([-np.pi*n*(n-1)/len(self.bb_freqs) for n in range(len(self.bb_freqs))])
        else:
            self.schroeder_phase_array = np.zeros_like(self.bb_freqs)
        self.num_steps = self.num_freqs * len(self.FREQS)
        self.low_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        self.num_retunes = len(self.FREQS)

        self.buffer_vector = np.arange(0, self.BUFF_SIZE, 1)
        self.bb_mixers = np.exp(-1j * 2 * np.pi * self.bb_freqs[:, None] * self.buffer_vector / self.Fs -1j * self.schroeder_phase_array[:, None])
        self.loopback_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        self.rx_buff = np.zeros_like(np.arange(0, self.BUFF_SIZE+self.BUFF_SIZE//self.CAPTURE_AVERAGES, 1), dtype=np.complex128)

        # self.range_profile_ring_buf = deque(maxlen=self.CAPTURE_AVERAGES)
        self.fastlock_load_times = []
        self.rx_destroy_buffer_times = []
        self.fastlock_recall_times = []
        self.rx_times = []
        self.range_profile_times = []

        # STARTUP Process:
        if self.verbose:
            print(f"[+] Bandwidth: {round(self.BW/1e6, 0)} MHz ({round((self.Fmin)/1e6, 0)} MHz - {round((self.Fmax)/1e6, 0)} MHz)")
            print(f"[+] Number of frequencies: {len(self.FREQS)}")
        if costas_mode:
            self.generate_costas_array()
            self.BW = self.Fs * len(self.step_order)
            self.FREQS.extend([max(self.FREQS)+(i+1)*self.Fs for i in range(len(self.step_order) - self.num_retunes)])
            self.FREQS = np.asarray(self.FREQS, dtype=np.int64)
            self.FREQS = self.FREQS[self.step_order]
            self.Fmax = max(self.FREQS)
            self.Fmin = min(self.FREQS)
            print(f"[+] Optimized Number of frequencies: {len(self.FREQS)}")
            self.num_retunes = len(self.step_order)
            self.num_steps = self.num_freqs * self.num_retunes
            print(len(self.FREQS), self.num_retunes)
            if self.verbose:
                print(f"[+] Optimized Bandwidth: {round(self.BW/1e6, 0)} MHz ({round((self.Fmin-self.Fs/2)/1e6, 0)} MHz - {round((self.Fmax+self.Fs/2)/1e6, 0)} MHz)")
                print("[+] Step Order (w/ Costas Array):", self.step_order)
        else:
            self.step_order = np.arange(0, self.num_retunes)
            if self.verbose:
                print("[+] Step Order (Linear):", self.step_order)
        self.S = np.zeros(self.num_steps, dtype=np.complex64)

        # AD936X Initialization
        self.sdr = adi.ad9361(uri=device_string)
        self.sdr.rx_enabled_channels = [rx_loopback_port, rx_port]
        self.sdr.tx_enabled_channels = [tx_port, tx_loopback_port]

        self.sdr.sample_rate = self.Fs
        self.sdr.rx_rf_bandwidth = self.Fs
        self.sdr.tx_rf_bandwidth = self.Fs
        self.sdr.rx_buffer_size = self.BUFF_SIZE + self.BUFF_SIZE // self.CAPTURE_AVERAGES

        self.sdr.gain_control_mode_chan0 = "manual"
        self.sdr.gain_control_mode_chan1 = "manual"
        self.sdr.rx_hardwaregain_chan0 = self.LOOPBACK_GAIN
        self.sdr.rx_hardwaregain_chan1 = self.RX_GAIN

        # -89.75–0 dB in 0.25 dB steps
        self.sdr.tx_hardwaregain_chan0 = self.TX_GAIN
        self.sdr.tx_hardwaregain_chan1 = -37.5
        self.sdr.tx_cyclic_buffer = True

        self.lo = self.sdr._ctrl.find_channel("altvoltage0", True)
        self.tx_lo = self.sdr._ctrl.find_channel("altvoltage1", True)

        self.store_fastlock_profiles()
        self.generate_baseband_tx()

    def store_fastlock_profiles(self):
        """
        Stores fastlock profiles for each frequency in self.FREQS. This method iterates over the frequencies, sets the SDR's RX LO to each frequency, and stores the corresponding fastlock profile. The profiles are saved in a list for later use.
        """
        for count, f in enumerate(self.FREQS):
            self.sdr.rx_lo = int(f)
            self.sdr.tx_lo = int(f)
            self.lo.attrs["fastlock_store"].value = "0"
            self.tx_lo.attrs["fastlock_store"].value = "0"
            self.fastlock_profiles = np.append(self.fastlock_profiles, self.lo.attrs["fastlock_save"].value.split(" ", 1)[1])
            self.tx_fastlock_profiles = np.append(self.tx_fastlock_profiles, self.tx_lo.attrs["fastlock_save"].value.split(" ", 1)[1])
            if self.verbose:
                print(f"[+] Storing Fastlock profiles: {count + 1}/{len(self.FREQS)} ({(count+1)/len(self.FREQS)*100:.1f}%)", end="\r")
        if self.verbose:
            print(f"\n[+] Stored {len(self.fastlock_profiles)} Fastlock profiles.")
        return

    def generate_baseband_tx(self, phase_offset=0, mag=1, verbose=False):
        self.tx_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        for n, f in enumerate(self.bb_freqs):
            if self.schroeder_phase:
                phi = self.schroeder_phase_array[n] + phase_offset
            else:
                phi = phase_offset
            self.tx_buff += np.exp(
                1j * (2 * np.pi * f * self.buffer_vector / self.Fs + phi)
            )
        self.tx_buff *= self.BB_GAIN * mag * self.TX_BB_SCALE / self.num_freqs
        self.tx_buff = self.tx_buff.astype(np.complex64)
        self.sdr.tx([self.tx_buff, self.tx_buff])
        if self.verbose and verbose:
            N = len(self.tx_buff)
            t = np.arange(N) / self.Fs
            X = np.fft.fftshift(np.fft.fft(self.tx_buff)) / N
            f = np.fft.fftshift(np.fft.fftfreq(N, 1 / self.Fs))
            fig, ax = plt.subplots(2, 1)
            ax[0].plot(t * 1e6, np.real(self.tx_buff))
            ax[0].set(xlabel="Time (µs)", ylabel="Amplitude")
            ax[1].plot(f / 1e6, 20 * np.log10(np.abs(X) + 1e-12))
            ax[1].set(xlabel="Frequency (MHz)", ylabel="Magnitude (dB)")
            plt.tight_layout()
            plt.show()
        return self.tx_buff

    def welch(self, p):
        """
        Welch construction of Costas array
        """
        for g in range(2, p):
            seq = [pow(g, k, p) for k in range(p - 1)]
            if len(set(seq)) == p - 1:
                return g, [x - 1 for x in seq]

    def euler_prime(self, n):
        """
        Euler's prime generating polynomial
        """
        return n**2 + n + 41

    def generate_costas_array(self):
        prime = min([i for i in self.low_primes if i > self.num_retunes], default=0)
        if not prime:
            for n in range(16):
                prime = self.euler_prime(n+1)
                if prime > self.num_retunes: break
        self.step_order = self.welch(prime)[1]
        self.descramble_order = np.argsort(self.step_order)
        return self.step_order

    def auto_optimize_gains(self, target_fraction=0.4, max_iterations=4):
        """Set both manual RX gains for good ADC headroom; TX gain is unchanged."""
        if not 0 < target_fraction < 1:
            raise ValueError("target_fraction must be between 0 and 1")
        gain_ranges = [
            (-1, 73) if f < 1.3e9 else (-3, 71) if f < 4e9 else (-10, 62)
            for f in self.FREQS
        ]
        gain_min = max(r[0] for r in gain_ranges)
        gain_max = min(r[1] for r in gain_ranges)
        target = target_fraction * (2 ** (self.SDR_BITS - 1) - 1)
        test_freq = self.FREQS[len(self.FREQS) // 2]

        self.sdr.rx_lo = test_freq
        self.sdr.tx_lo = test_freq
        time.sleep(self.retune_delay)

        for _ in range(max_iterations):
            self.sdr.rx_destroy_buffer()
            self.sdr.rx()  # discard the first buffer after tuning/gain changes
            loop_raw, rx_raw = self.sdr.rx()
            peaks = [
                np.quantile(np.maximum(np.abs(x.real), np.abs(x.imag)), 0.999)
                for x in (loop_raw, rx_raw)
            ]
            if min(peaks) <= 0:
                raise RuntimeError("Cannot optimize gains: an RX channel has no signal")

            old_gains = [self.LOOPBACK_GAIN, self.RX_GAIN]
            new_gains = [
                int(np.clip(round(g + 20 * np.log10(target / p)), gain_min, gain_max))
                for g, p in zip(old_gains, peaks)
            ]
            self.LOOPBACK_GAIN, self.RX_GAIN = new_gains
            self.sdr.rx_hardwaregain_chan0 = self.LOOPBACK_GAIN
            self.sdr.rx_hardwaregain_chan1 = self.RX_GAIN
            if new_gains == old_gains:
                break
            time.sleep(self.retune_delay)

        self.sdr.rx_destroy_buffer()
        loop_raw, rx_raw = self.sdr.rx()
        peaks = [
            np.quantile(np.maximum(np.abs(x.real), np.abs(x.imag)), 0.999)
            for x in (loop_raw, rx_raw)
        ]
        return {
            "loopback_gain_db": self.LOOPBACK_GAIN,
            "rx_gain_db": self.RX_GAIN,
            "loopback_peak_fraction": peaks[0] / (2 ** (self.SDR_BITS - 1) - 1),
            "rx_peak_fraction": peaks[1] / (2 ** (self.SDR_BITS - 1) - 1),
        }

    def calibrate(self, num_samples=20, output_path="calibration.npy"):
        """
        Capture fresh empty-scene complex range profiles for later envelope
        averaging by the backprojection function.
        
        Parameters:
        num_samples (int): Number of fresh sweeps to average.
        output_path (path-like or None): Where to save the complex profile.
        
        Returns:
        numpy.ndarray: A 2D list of complex calibration range profiles.
        """
        if not isinstance(num_samples, int) or num_samples <= 0:
            raise ValueError("num_samples must be a positive integer")

        calibration_profiles = np.empty(
            (num_samples, self.num_steps), dtype=np.complex128
        )
        for sample_index in range(num_samples):
            self.sweep()
            _, rp = self.get_range_profile(plot=False, cal=False)
            calibration_profiles[sample_index] = rp
        if output_path is not None:
            np.save(output_path, calibration_profiles)
        self.calibration_profiles = calibration_profiles
        self.cal = np.mean(calibration_profiles, axis=0)
        return calibration_profiles

    def extract_bb_phasors(self):
        mini_buff = self.BUFF_SIZE // self.CAPTURE_AVERAGES
        numerator = np.zeros(self.num_freqs, dtype=complex)
        denominator = np.zeros(self.num_freqs)
        t0 = time.perf_counter()
        loop_raw, rx_raw = self.sdr.rx()
        dt = time.perf_counter() - t0
        self.rx_times.append(dt)
        loop_raw = loop_raw[mini_buff:]
        rx_raw = rx_raw[mini_buff:]

        for i in range(self.CAPTURE_AVERAGES):
            a = i * mini_buff
            b = a + mini_buff
            mixers = self.bb_mixers[:, a:b]
            loop_phasors = mixers @ loop_raw[a:b] / mini_buff
            rx_phasors = mixers @ rx_raw[a:b] / mini_buff

            numerator += rx_phasors * np.conj(loop_phasors)
            denominator += np.abs(loop_phasors) ** 2

        return numerator / (denominator + 1e-12)

    def load_fastlock(self, start_idx):
        t0 = time.perf_counter()
        # self.sdr.rx_destroy_buffer()
        dt = time.perf_counter() - t0
        self.rx_destroy_buffer_times.append(dt)

        t0 = time.perf_counter()
        rx_profiles = self.fastlock_profiles[start_idx:start_idx + 8]
        tx_profiles = self.tx_fastlock_profiles[start_idx:start_idx + 8]
        for i, (rx_profile, tx_profile) in enumerate(zip(rx_profiles, tx_profiles)):
            self.lo.attrs["fastlock_load"].value = f"{i} {rx_profile}"
            self.tx_lo.attrs["fastlock_load"].value = f"{i} {tx_profile}"
        dt = time.perf_counter() - t0
        self.fastlock_load_times.append(dt)

    def retune(self, freq, register_num):
        t0 = time.perf_counter()
        self.lo.attrs["fastlock_recall"].value = str(register_num)
        self.tx_lo.attrs["fastlock_recall"].value = str(register_num)
        dt = time.perf_counter() - t0
        self.fastlock_recall_times.append(dt)

    def sweep(self):
        self.fastlock_load_times.clear()
        self.rx_destroy_buffer_times.clear()
        self.fastlock_recall_times.clear()
        self.rx_times.clear()
        self.range_profile_times.clear()
        range_profile_t0 = time.perf_counter()
        for count, freq in enumerate(self.FREQS):
            if count % 8 == 0:
                if self.verbose:
                    print(f"[-] Loading Fastlock profiles for {freq} - {self.FREQS[min(count + 7, len(self.FREQS) - 1)]}")
                self.load_fastlock(start_idx=count)
            self.retune(freq, count % 8)
            time.sleep(self.retune_delay)
            phasors = self.extract_bb_phasors()
            if self.costas_mode:
                self.S[self.step_order[count]*self.num_freqs:(self.step_order[count]+1)*self.num_freqs] = phasors
            else:
                self.S[count*self.num_freqs:(count+1)*self.num_freqs] = phasors

        self.range_profile_times.append(time.perf_counter() - range_profile_t0)
        if self.verbose:
            print(f"{'Operation':<24} {'Average (ms)':>12} {'Max (ms)':>12} {'Measures':>10}")
            print("-" * 61)
            for label, measurements in (
                ("Fastlock load", self.fastlock_load_times),
                ("RX buffer destroy", self.rx_destroy_buffer_times),
                ("Fastlock recall", self.fastlock_recall_times),
                ("SDR RX", self.rx_times),
                ("Range profile capture", self.range_profile_times),
            ):
                print(
                    f"{label:<24} {np.mean(measurements) * 1e3:>12.3f} "
                    f"{max(measurements) * 1e3:>12.3f} {len(measurements):>10}"
                )

    def get_range_profile(self, plot=False, cal=False):
        if np.mean(self.S) == 0: self.sweep()
        S = self.S.copy()
        S = S - np.mean(S)
        S = S * np.hanning(self.num_steps)
        rp = np.fft.ifft(S)

        if cal is not False and cal is not None:
            if cal is True:
                if not hasattr(self, "cal"):
                    raise RuntimeError(
                        "No calibration is loaded; call calibrate() first"
                    )
                calibration = np.asarray(self.cal)
            elif isinstance(cal, (str, bytes)) or hasattr(cal, "__fspath__"):
                calibration = np.load(cal, allow_pickle=False)
            else:
                calibration = np.asarray(cal)
            if calibration.shape != rp.shape:
                raise ValueError(
                    f"Calibration shape {calibration.shape} does not match "
                    f"range profile shape {rp.shape}"
                )
            rp -= calibration

        # Keep rp complex for coherent SAR processing.  Only magnitude data is
        # converted to dB for plotting; log10(complex) is not display data.
        rp_db = 20 * np.log10(np.abs(rp) + 1e-12)

        range_axis = (
            np.arange(self.num_steps)
            * self.C
            / (2 * self.num_steps * self.BB_SPACING)
        )
        if plot:
            fig, ax = plt.subplots(figsize=(11, 5))
            ax.plot(range_axis, rp_db, color="blue", label="Range Profile")
            ax.set_title("Stepped-CW Range Profile")
            ax.set_xlabel("Range (m)")
            ax.set_ylabel("Magnitude (dB)")
            ax.set_ylim(-60, 0)
            ax.set_xlim(0, self.max_range)
            ax.grid(True)
            # plt.tight_layout()
            # plt.legend()
            plt.savefig("/Users/levifarinas/Library/Mobile Documents/com~apple~CloudDocs/Projects/SAR Backprojection/Radar Hardware/SFCW/IMG/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png", dpi=300)
        return range_axis, rp

    def sweep_average(self, averages=5):
        S_sum = np.zeros_like(self.S, dtype=np.complex128)
        for _ in range(averages):
            self.sweep()
            S_sum += self.S
        self.S = (S_sum / averages).astype(np.complex64)


# if __name__ == "__main__":
#     sfcw = SFCWRadar()
