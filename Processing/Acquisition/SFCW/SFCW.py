import numpy as np
import adi
import matplotlib.pyplot as plt
from datetime import datetime
import time

class SFCWRadar:
    def __init__(self, device_string="usb:", Fmin=600e6, Fmax=300e6, verbose=True, Fs=20e6):
        self.sdr = adi.ad9361(uri=device_string)
        self.sdr.rx_enabled_channels = [0, 1]
        self.sdr.tx_enabled_channels = [0, 1]

        self.RX_GAIN = 71
        self.LOOPBACK_GAIN = 71
        self.TX_GAIN = 0
        self.BUFF_SIZE = 8192
        self.BB_GAIN = 1
        self.SDR_BITS = 12
        self.C = 3e8
        self.TX_BB_SCALE = 2**14
        self.BB_SPACING = 2e6
        self.CAPTURE_AVERAGES = 3
        self.Fs = int(Fs)
        self.max_range = self.C / (2 * self.BB_SPACING)
        self.retune_delay = 100e-6

    
        self.verbose = True if verbose else False
        self.Fmin = Fmin
        self.Fmax = Fmax
        self.BW = Fmax - Fmin
        if self.BW <= 0:
            raise ValueError("Fmax must be greater than Fmin")
        
        self.sdr.sample_rate = self.Fs
        self.sdr.rx_rf_bandwidth = self.Fs
        self.sdr.tx_rf_bandwidth = self.Fs
        self.sdr.rx_buffer_size = self.BUFF_SIZE

        self.sdr.gain_control_mode_chan0 = "manual"
        self.sdr.gain_control_mode_chan1 = "manual"
        self.sdr.rx_hardwaregain_chan0 = self.LOOPBACK_GAIN
        self.sdr.rx_hardwaregain_chan1 = self.RX_GAIN

        # -89.75–0 dB in 0.25 dB steps
        self.sdr.tx_hardwaregain_chan0 = self.TX_GAIN
        self.sdr.tx_hardwaregain_chan1 = -37.5

        self.FREQS = [int(i) for i in np.arange(self.Fmin, self.Fmax, self.Fs)]
        self.fastlock_profiles = np.array([])
        self.num_freqs = int(self.Fs // self.BB_SPACING)
        self.bb_freqs = np.arange(
            -self.Fs / 2,
            self.Fs / 2,
            self.BB_SPACING
        )
        self.num_steps = self.num_freqs*len(self.FREQS)

        self.buffer_vector = np.arange(0, self.BUFF_SIZE, 1)
        self.loopback_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        self.rx_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        self.S = np.zeros(self.num_freqs * len(self.FREQS), dtype=np.complex64)

        self.sdr.tx_cyclic_buffer = True
        self.lo = self.sdr._ctrl.find_channel("altvoltage0", True)

        # STARTUP Process:
        self.store_fastlock_profiles()
        self.generate_baseband_tx()


    def store_fastlock_profiles(self):
        """
        Stores fastlock profiles for each frequency in self.FREQS. This method iterates over the frequencies, sets the SDR's RX LO to each frequency, and stores the corresponding fastlock profile. The profiles are saved in a list for later use.
        """
        for count, f in enumerate(self.FREQS):
            self.sdr.rx_lo = f
            self.lo.attrs["fastlock_store"].value = "0"
            self.fastlock_profiles = np.append(self.fastlock_profiles, self.lo.attrs["fastlock_save"].value.split(" ", 1)[1])
            if self.verbose:
                print(f"[-] Storing Fastlock profiles: {count + 1}/{len(self.FREQS)} ({(count+1)/len(self.FREQS)*100:.1f}%)", end="\r")
        if self.verbose:
            print(f"\n[-] Stored {len(self.fastlock_profiles)} Fastlock profiles.")
        return

    def generate_baseband_tx(self, phase=0, mag=1, verbose=False):
        self.tx_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        for bb_freq in self.bb_freqs:
            # print(self.buffer_vector)
            self.tx_buff += np.exp(
                1j * (2 * np.pi * bb_freq * self.buffer_vector / self.Fs + phase)
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
        corrected = np.zeros(self.num_freqs, dtype=complex)
        for _ in range(self.CAPTURE_AVERAGES):
            loop_raw, rx_raw = self.sdr.rx()
            loop_phasors = np.zeros(self.num_freqs, dtype=complex)
            rx_phasors = np.zeros(self.num_freqs, dtype=complex)
            for i, f in enumerate(self.bb_freqs):
                mixer = np.exp(-1j * 2 * np.pi * f * self.buffer_vector / self.Fs)
                loop_phasors[i] = np.mean(loop_raw * mixer)
                rx_phasors[i] = np.mean(rx_raw * mixer)
            corrected += rx_phasors / (loop_phasors + 1e-12)
        return corrected / self.CAPTURE_AVERAGES

    # def extract_bb_phasors(self):
    #     loop_phasors = np.zeros(self.num_freqs, dtype=complex)
    #     rx_phasors = np.zeros(self.num_freqs, dtype=complex)
    #     for _ in range(self.CAPTURE_AVERAGES):
    #         try:
    #             loop_raw, rx_raw = self.sdr.rx()
    #             for i, f in enumerate(self.bb_freqs):
    #                 mixer = np.exp(-1j * 2 * np.pi * f * self.buffer_vector / self.Fs)
    #                 loop_phasors[i] += np.mean(loop_raw * mixer)
    #                 rx_phasors[i] += np.mean(rx_raw * mixer)
    #         except:
    #             pass
    #     loop_phasors /= self.CAPTURE_AVERAGES
    #     rx_phasors /= self.CAPTURE_AVERAGES
    #     return rx_phasors / (loop_phasors + 1e-12)

    def load_fastlock(self, start_idx):
        self.sdr.rx_destroy_buffer()
        profiles = self.fastlock_profiles[start_idx:start_idx + 8]
        for i, profile in enumerate(profiles):
            self.lo.attrs["fastlock_load"].value = f"{i} {profile}"

    # def retune(self, register_num):
    #     register_num = int(register_num)
    #     if not 0 <= register_num <= 7:
    #         raise ValueError(f"Invalid fastlock slot: {register_num}")
    #     self.lo.attrs["fastlock_recall"].value = str(register_num)
    def retune(self, freq, register_num):
        self.lo.attrs["fastlock_recall"].value = str(register_num)
        self.sdr.tx_lo = int(freq)


    def sweep(self):
        for count, freq in enumerate(self.FREQS):
            if count % 8 == 0:
                if self.verbose:
                    print(f"[-] Loading Fastlock profiles for {freq} - {self.FREQS[min(count + 7, len(self.FREQS) - 1)]}")
                self.load_fastlock(start_idx=count)
            self.retune(freq, count % 8)
            time.sleep(self.retune_delay)
            phasors = self.extract_bb_phasors()
            self.S[count*self.num_freqs:(count+1)*self.num_freqs] = phasors
        # try:
        #     self.sdr.tx_destroy_buffer()
        # except Exception:
        #     pass

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
