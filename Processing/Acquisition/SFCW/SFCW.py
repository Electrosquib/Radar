import numpy as np
import matplotlib.pyplot as plt # type: ignore
import argparse
from datetime import datetime
import time
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import shutil
import shlex
import struct
import subprocess
import weakref


class PSControllerError(RuntimeError):
    """Raised when the Zynq PS acquisition controller cannot be used."""


class _ControllerCleanupProxy:
    """Compatibility surface for callers that only destroy pyadi buffers."""

    def __init__(self, radar):
        self._radar = weakref.ref(radar)
        self._destroyed = set()

    def _mark_destroyed(self, name):
        self._destroyed.add(name)
        radar = self._radar()
        if radar is not None and self._destroyed == {"rx", "tx"}:
            radar.close()

    def rx_destroy_buffer(self):
        self._mark_destroyed("rx")

    def tx_destroy_buffer(self):
        self._mark_destroyed("tx")

    def close(self):
        radar = self._radar()
        if radar is not None:
            radar.close()


class _PSController:
    MAGIC = b"SFCW"
    VERSION = 1
    CONFIGURE = 1
    SWEEP = 2
    PING = 3
    SHUTDOWN = 4
    HEADER = struct.Struct("<4sHHIQ")
    CONFIG = struct.Struct("<11I3i5d")
    TIMING = struct.Struct("<HBBIIiQ")
    SWEEP_PREFIX = struct.Struct("<5IQ")
    TIMING_NAMES = {
        1: "Full retune",
        2: "Fastlock store",
        3: "Fastlock save",
        4: "Fastlock load",
        5: "Fastlock recall",
        6: "Buffer refill",
    }
    SIDE_NAMES = {0: "", 1: "RX", 2: "TX"}

    def __init__(
        self,
        host,
        port,
        user,
        password,
        key_filename,
        cross_compiler,
        remote_binary,
        timeout=15,
    ):
        self.host = host
        self.remote_binary = remote_binary
        self._ssh = None
        self._channel = None
        self._stdin = None
        self._stdout = None
        try:
            import paramiko  # type: ignore
        except ImportError as exc:
            raise PSControllerError(
                "Paramiko is required for PS control; install project dependencies "
                "or set use_ps_controller=False"
            ) from exc

        binary = self._ensure_local_binary(cross_compiler)
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                key_filename=key_filename,
                timeout=timeout,
                auth_timeout=timeout,
                banner_timeout=timeout,
                allow_agent=True,
                look_for_keys=True,
            )
            self._ssh = client
            self._deploy_if_needed(binary)
            transport = client.get_transport()
            if transport is None:
                raise PSControllerError("SSH transport was not established")
            channel = transport.open_session(timeout=timeout)
            channel.exec_command(f"{shlex.quote(remote_binary)} --stdio")
            self._channel = channel
            self._stdin = channel.makefile("wb", 0)
            self._stdout = channel.makefile("rb", 0)
            payload = self._request(self.PING)
            if len(payload) != 4 or struct.unpack("<I", payload)[0] != self.VERSION:
                raise PSControllerError("PS controller protocol negotiation failed")
        except Exception as exc:
            stderr_detail = self._stderr_text()
            self.close(force=True)
            if isinstance(exc, PSControllerError):
                if stderr_detail:
                    raise PSControllerError(f"{exc}; remote stderr: {stderr_detail}") from exc
                raise
            raise PSControllerError(
                f"Could not start PS controller on {host}: {exc}. "
                + (f"Remote stderr: {stderr_detail}. " if stderr_detail else "")
                + "Fix build/SSH access or set use_ps_controller=False"
            ) from exc

    @staticmethod
    def _apps_directory():
        return Path(__file__).resolve().parents[2] / "Firmware" / "Apps"

    @classmethod
    def _ensure_local_binary(cls, cross_compiler):
        apps = cls._apps_directory()
        binary = apps / "SFCW"
        inputs = [apps / "SFCW.c", apps / "Makefile"]
        stale = not binary.exists() or any(
            path.stat().st_mtime_ns > binary.stat().st_mtime_ns for path in inputs
        )
        if not stale:
            return binary

        compiler = cross_compiler or os.environ.get("SFCW_CC")
        if compiler:
            compiler = shutil.which(compiler) or compiler
        else:
            compiler = next(
                (
                    found
                    for name in (
                        "armv7-unknown-linux-gnueabihf-gcc",
                        "armv7-linux-gnueabihf-gcc",
                        "arm-linux-gnueabihf-gcc",
                        "arm-none-linux-gnueabihf-gcc",
                    )
                    if (found := shutil.which(name))
                ),
                None,
            )
        if not compiler:
            raise PSControllerError(
                "The ARM SFCW controller is missing or stale and no cross-compiler "
                "was found. Set ps_cross_compiler or SFCW_CC, or set "
                "use_ps_controller=False"
            )
        try:
            subprocess.run(
                ["make", "build", f"CC={compiler}"],
                cwd=apps,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise PSControllerError(
                f"Failed to cross-build {apps / 'SFCW.c'}: {exc}. "
                "Set use_ps_controller=False to use legacy pyadi control"
            ) from exc
        if not binary.exists():
            raise PSControllerError("Cross-build completed without producing Firmware/Apps/SFCW")
        return binary

    @staticmethod
    def _hash_file(file_object):
        digest = hashlib.sha256()
        while True:
            chunk = file_object.read(1024 * 1024)
            if not chunk:
                return digest.digest()
            digest.update(chunk)

    def _deploy_if_needed(self, binary):
        local_hash = hashlib.sha256(binary.read_bytes()).digest()
        sftp = self._ssh.open_sftp()
        try:
            try:
                with sftp.open(self.remote_binary, "rb") as remote:
                    remote_hash = self._hash_file(remote)
            except OSError:
                remote_hash = None
            if remote_hash == local_hash:
                return
            temporary = self.remote_binary + f".tmp.{os.getpid()}"
            sftp.put(str(binary), temporary)
            sftp.chmod(temporary, 0o755)
            try:
                sftp.posix_rename(temporary, self.remote_binary)
            except (AttributeError, OSError):
                try:
                    sftp.remove(self.remote_binary)
                except OSError:
                    pass
                sftp.rename(temporary, self.remote_binary)
        finally:
            sftp.close()

    @staticmethod
    def _read_exact(stream, length):
        chunks = []
        remaining = length
        while remaining:
            chunk = stream.read(remaining)
            if not chunk:
                raise PSControllerError("PS controller closed its output unexpectedly")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def _stderr_text(self):
        if self._channel is None or not self._channel.recv_stderr_ready():
            return ""
        return self._channel.recv_stderr(65536).decode("utf-8", "replace").strip()

    def _request(self, message_type, payload=b""):
        if self._stdin is None or self._stdout is None:
            raise PSControllerError("PS controller is closed")
        self._stdin.write(
            self.HEADER.pack(self.MAGIC, self.VERSION, message_type, 0, len(payload))
        )
        if payload:
            self._stdin.write(payload)
        self._stdin.flush()
        header = self.HEADER.unpack(self._read_exact(self._stdout, self.HEADER.size))
        magic, version, response_type, status, length = header
        if magic != self.MAGIC or version != self.VERSION or response_type != message_type:
            raise PSControllerError("Malformed or incompatible PS controller response")
        response = self._read_exact(self._stdout, length)
        if status:
            detail = response.decode("utf-8", "replace") or self._stderr_text()
            raise PSControllerError(f"PS controller command {message_type} failed: {detail}")
        return response

    @classmethod
    def decode_timings(cls, payload, count, offset=0):
        records = []
        for _ in range(count):
            end = offset + cls.TIMING.size
            if end > len(payload):
                raise PSControllerError("Truncated timing records from PS controller")
            operation, side, slot, index, detail, status, duration_ns = (
                cls.TIMING.unpack_from(payload, offset)
            )
            records.append(
                {
                    "operation_id": operation,
                    "operation": cls.TIMING_NAMES.get(operation, f"Operation {operation}"),
                    "side": cls.SIDE_NAMES.get(side, f"Side {side}"),
                    "slot": None if slot == 255 else slot,
                    "frequency_index": index,
                    "detail": detail,
                    "status": status,
                    "duration_s": duration_ns / 1e9,
                }
            )
            offset = end
        return records, offset

    def configure(self, radar, rx_port, rx_loopback_port, tx_port, tx_loopback_port):
        flags = int(radar.schroeder_phase) | (
            int(radar.collect_controller_timings) << 1
        )
        payload = self.CONFIG.pack(
            flags,
            radar.Fs,
            radar.Fs,
            radar.BUFF_SIZE,
            radar.CAPTURE_AVERAGES,
            int(round(radar.retune_delay * 1e6)),
            radar.num_retunes,
            rx_port,
            rx_loopback_port,
            tx_port,
            tx_loopback_port,
            radar.RX_GAIN,
            radar.LOOPBACK_GAIN,
            radar.TX_GAIN,
            -37.5,
            radar.BB_SPACING,
            radar.BB_GAIN * radar.tx_magnitude,
            radar.TX_BB_SCALE,
            radar.tx_phase_offset,
        ) + np.asarray(radar.FREQS, dtype="<u8").tobytes()
        response = self._request(self.CONFIGURE, payload)
        if len(response) < 4:
            raise PSControllerError("Truncated configure response")
        count = struct.unpack_from("<I", response)[0]
        records, offset = self.decode_timings(response, count, 4)
        if offset != len(response):
            raise PSControllerError("Unexpected trailing configure data")
        return records

    def sweep(self):
        response = self._request(self.SWEEP)
        if len(response) < self.SWEEP_PREFIX.size:
            raise PSControllerError("Truncated sweep response")
        retunes, averages, samples, channels, timing_count, acquisition_ns = (
            self.SWEEP_PREFIX.unpack_from(response)
        )
        if channels != 2:
            raise PSControllerError(f"Expected two RX channels, received {channels}")
        timings, offset = self.decode_timings(
            response, timing_count, self.SWEEP_PREFIX.size
        )
        expected_values = retunes * averages * samples * 4
        raw = np.frombuffer(response, dtype="<i2", count=expected_values, offset=offset)
        if raw.size != expected_values or offset + expected_values * 2 != len(response):
            raise PSControllerError("Raw IQ payload has an unexpected size")
        return (
            raw.reshape(retunes, averages, samples, 4).copy(),
            timings,
            acquisition_ns / 1e9,
        )

    def close(self, force=False):
        if not force and self._stdin is not None and self._stdout is not None:
            try:
                self._request(self.SHUTDOWN)
            except Exception:
                pass
        for stream_name in ("_stdin", "_stdout"):
            stream = getattr(self, stream_name, None)
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    pass
                setattr(self, stream_name, None)
        if self._channel is not None:
            self._channel.close()
            self._channel = None
        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None

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
            costas_mode=True,
            schroeder_phase=True,
            tx_phase_offset=0.0,
            tx_magnitude=1.0,
            use_ps_controller=True,
            collect_controller_timings=False,
            ps_host="192.168.2.1",
            ps_port=22,
            ps_user="root",
            ps_password="analog",
            ps_key_filename=None,
            ps_cross_compiler=None,
            ps_remote_binary="/root/SFCW",
        ):
        self.RX_GAIN = 71
        self.LOOPBACK_GAIN = 0
        self.TX_GAIN = 0
        self.BUFF_SIZE = 400 # 20e6 / 1e6 = 20 samps. 8192 / 20 = 409.6. Must be an integer multiple to prevent spectral leakage
        self.BB_GAIN = 1
        self.SDR_BITS = 12
        self.C = 3e8
        self.TX_BB_SCALE = 2**14
        self.BB_SPACING = 2e6
        self.CAPTURE_AVERAGES = 4
        self.Fs = int(Fs)
        self.max_range = self.C / (2 * self.BB_SPACING)
        self.retune_delay = 100e-6

    
        self.verbose = True if verbose else False
        self.costas_mode = True if costas_mode else False
        self.schroeder_phase = True if schroeder_phase else False
        self.tx_phase_offset = float(tx_phase_offset)
        self.tx_magnitude = float(tx_magnitude)
        if not np.isfinite(self.tx_phase_offset):
            raise ValueError("tx_phase_offset must be finite")
        if not np.isfinite(self.tx_magnitude) or self.tx_magnitude < 0:
            raise ValueError("tx_magnitude must be finite and nonnegative")
        self.use_ps_controller = bool(use_ps_controller)
        self.collect_controller_timings = bool(collect_controller_timings)
        self._controller = None
        self._closed = False
        self._ps_ports = (rx_port, rx_loopback_port, tx_port, tx_loopback_port)
        self._controller_signature = None

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
        self.num_steps = self.num_freqs * len(self.FREQS)
        self.low_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        self.num_retunes = len(self.FREQS)

        self.buffer_vector = np.arange(0, self.BUFF_SIZE, 1)
        self.bb_mixers = np.exp(-1j * 2 * np.pi * self.bb_freqs[:, None] * self.buffer_vector / self.Fs)
        self.loopback_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        self.rx_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)

        self.range_profile_ring_buf = deque(maxlen=self.CAPTURE_AVERAGES)
        self.fastlock_load_times = []
        self.rx_destroy_buffer_times = []
        self.fastlock_recall_times = []
        self.rx_times = []
        self.range_profile_times = []
        self.controller_initialization_timings = []
        self.controller_timings = []
        self.controller_acquisition_times = []
        self.controller_transfer_times = []
        self.host_processing_times = []

        # STARTUP Process:
        if self.verbose:
            print(f"[+] Bandwidth: {round(self.BW/1e6, 0)} MHz ({round(self.Fmin/1e6, 0)} MHz - {round(self.Fmax/1e6, 0)} MHz)")
        if costas_mode:
            self.generate_costas_array()
            self.BW = self.Fs * len(self.step_order)
            self.FREQS.extend([max(self.FREQS)+(i+1)*self.Fs for i in range(len(self.step_order) - self.num_retunes)])
            self.FREQS = np.asarray(self.FREQS, dtype=np.int64)
            self.FREQS = self.FREQS[self.step_order]
            self.num_retunes = len(self.step_order)
            self.num_steps = self.num_freqs * self.num_retunes
            if self.verbose:
                print("[+] Frequency order:", self.FREQS)
                print(f"[+] Optimized Bandwidth: {round(self.BW/1e6, 0)} MHz ({round(self.Fmin/1e6, 0)} MHz - {round(self.Fmax/1e6, 0)} MHz)")
                print("[+] Step Order (w/ Costas Array):", self.step_order)
        else:
            self.step_order = np.arange(0, self.num_retunes)
            if self.verbose:
                print("[+] Step Order (Linear):", self.step_order)
        self.S = np.zeros(self.num_steps, dtype=np.complex64)

        if self.use_ps_controller:
            self.sdr = _ControllerCleanupProxy(self)
            self.lo = None
            self.tx_lo = None
            self.generate_baseband_tx(
                phase_offset=self.tx_phase_offset,
                mag=self.tx_magnitude,
                transmit=False,
            )
            self._controller = _PSController(
                host=ps_host,
                port=ps_port,
                user=ps_user,
                password=ps_password,
                key_filename=ps_key_filename,
                cross_compiler=ps_cross_compiler,
                remote_binary=ps_remote_binary,
            )
            try:
                self.controller_initialization_timings = self._controller.configure(
                    self,
                    *self._ps_ports,
                )
                self._controller_signature = self._ps_config_signature()
            except Exception:
                self._controller.close(force=True)
                self._controller = None
                raise
            if self.verbose:
                print("[+] Zynq PS SFCW controller configured")
                self._print_timing_summary(self.controller_initialization_timings)
        else:
            # Legacy host-driven pyadi path.
            try:
                import adi  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "pyadi-iio is required when use_ps_controller=False"
                ) from exc
            self.sdr = adi.ad9361(uri=device_string)
            self.sdr.rx_enabled_channels = [rx_loopback_port, rx_port]
            self.sdr.tx_enabled_channels = [tx_port, tx_loopback_port]
            self.sdr.sample_rate = self.Fs
            self.sdr.rx_rf_bandwidth = self.Fs
            self.sdr.tx_rf_bandwidth = self.Fs
            self.sdr.rx_buffer_size = self.BUFF_SIZE
            self.sdr.gain_control_mode_chan0 = "manual"
            self.sdr.gain_control_mode_chan1 = "manual"
            self.sdr.rx_hardwaregain_chan0 = self.LOOPBACK_GAIN
            self.sdr.rx_hardwaregain_chan1 = self.RX_GAIN
            self.sdr.tx_hardwaregain_chan0 = self.TX_GAIN
            self.sdr.tx_hardwaregain_chan1 = -37.5
            self.sdr.tx_cyclic_buffer = True
            self.lo = self.sdr._ctrl.find_channel("altvoltage0", True)
            self.tx_lo = self.sdr._ctrl.find_channel("altvoltage1", True)
            self.store_fastlock_profiles()
            self.generate_baseband_tx(
                phase_offset=self.tx_phase_offset,
                mag=self.tx_magnitude,
            )

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
                print(f"[-] Storing Fastlock profiles: {count + 1}/{len(self.FREQS)} ({(count+1)/len(self.FREQS)*100:.1f}%)", end="\r")
        if self.verbose:
            print(f"\n[-] Stored {len(self.fastlock_profiles)} Fastlock profiles.")
        return

    def generate_baseband_tx(self, phase_offset=0, mag=1, verbose=False, transmit=True):
        if self.use_ps_controller and transmit:
            self.tx_phase_offset = float(phase_offset)
            self.tx_magnitude = float(mag)
            transmit = False
        self.tx_buff = np.zeros_like(self.buffer_vector, dtype=np.complex128)
        for n, f in enumerate(self.bb_freqs):
            if self.schroeder_phase:
                phi = -np.pi*n*(n-1)/len(self.bb_freqs) + phase_offset
            else:
                phi = phase_offset
            self.tx_buff += np.exp(
                1j * (2 * np.pi * f * self.buffer_vector / self.Fs + phi)
            )
        self.tx_buff *= self.BB_GAIN * mag * self.TX_BB_SCALE / self.num_freqs
        self.tx_buff = self.tx_buff.astype(np.complex64)
        if transmit:
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
        if self.use_ps_controller:
            raise RuntimeError(
                "auto_optimize_gains() requires step-at-a-time pyadi access; "
                "construct SFCWRadar(use_ps_controller=False) for this operation"
            )
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
        if self.use_ps_controller:
            raise RuntimeError(
                "extract_bb_phasors() is internal to a complete PS-controlled sweep; "
                "use sweep() or construct with use_ps_controller=False"
            )
        numerator = np.zeros(self.num_freqs, dtype=complex)
        denominator = np.zeros(self.num_freqs)
        for _ in range(self.CAPTURE_AVERAGES):
            t0 = time.perf_counter()
            loop_raw, rx_raw = self.sdr.rx()
            dt = time.perf_counter() - t0
            self.rx_times.append(dt)
            loop_phasors = self.bb_mixers @ loop_raw / self.BUFF_SIZE
            rx_phasors = self.bb_mixers @ rx_raw / self.BUFF_SIZE
            numerator += rx_phasors * np.conj(loop_phasors)
            denominator += np.abs(loop_phasors) ** 2
        return numerator / (denominator + 1e-12)

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
        if self.use_ps_controller:
            raise RuntimeError(
                "load_fastlock() is not a host round-trip operation in PS mode; "
                "use sweep() or construct with use_ps_controller=False"
            )
        t0 = time.perf_counter()
        self.sdr.rx_destroy_buffer()
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

    # def retune(self, register_num):
    #     register_num = int(register_num)
    #     if not 0 <= register_num <= 7:
    #         raise ValueError(f"Invalid fastlock slot: {register_num}")
    #     self.lo.attrs["fastlock_recall"].value = str(register_num)
    def retune(self, freq, register_num):
        if self.use_ps_controller:
            raise RuntimeError(
                "retune() is managed inside the timing-critical PS sweep; "
                "use sweep() or construct with use_ps_controller=False"
            )
        t0 = time.perf_counter()
        self.lo.attrs["fastlock_recall"].value = str(register_num)
        self.tx_lo.attrs["fastlock_recall"].value = str(register_num)
        dt = time.perf_counter() - t0
        self.fastlock_recall_times.append(dt)


    def sweep(self):
        if self.use_ps_controller:
            return self._sweep_with_ps_controller()
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

    @staticmethod
    def _print_timing_summary(records):
        if not records:
            return
        grouped = {}
        for record in records:
            key = " ".join(
                part for part in (record["side"], record["operation"]) if part
            )
            grouped.setdefault(key, []).append(record["duration_s"])
        print(f"{'PS operation':<24} {'Average (ms)':>12} {'Max (ms)':>12} {'Measures':>10}")
        print("-" * 61)
        for label, measurements in grouped.items():
            print(
                f"{label:<24} {np.mean(measurements) * 1e3:>12.3f} "
                f"{max(measurements) * 1e3:>12.3f} {len(measurements):>10}"
            )

    def _ps_config_signature(self):
        return (
            self.Fs,
            self.BUFF_SIZE,
            self.CAPTURE_AVERAGES,
            self.retune_delay,
            self.BB_SPACING,
            self.BB_GAIN,
            self.TX_BB_SCALE,
            self.tx_phase_offset,
            self.tx_magnitude,
            self.RX_GAIN,
            self.LOOPBACK_GAIN,
            self.TX_GAIN,
            self.schroeder_phase,
            self.collect_controller_timings,
            tuple(map(int, self.FREQS)),
            self._ps_ports,
        )

    def _sweep_with_ps_controller(self):
        if self._controller is None:
            raise PSControllerError("PS controller is not connected")
        signature = self._ps_config_signature()
        if signature != self._controller_signature:
            self.generate_baseband_tx(
                phase_offset=self.tx_phase_offset,
                mag=self.tx_magnitude,
                transmit=False,
            )
            self.controller_initialization_timings = self._controller.configure(
                self, *self._ps_ports
            )
            self._controller_signature = signature
        request_started = time.perf_counter()
        raw, timings, acquisition_seconds = self._controller.sweep()
        request_seconds = time.perf_counter() - request_started
        processing_started = time.perf_counter()

        loopback = raw[..., 0].astype(np.float32) + 1j * raw[..., 1].astype(np.float32)
        received = raw[..., 2].astype(np.float32) + 1j * raw[..., 3].astype(np.float32)
        loop_phasors = np.einsum(
            "ks,ras->rak", self.bb_mixers, loopback, optimize=True
        ) / self.BUFF_SIZE
        rx_phasors = np.einsum(
            "ks,ras->rak", self.bb_mixers, received, optimize=True
        ) / self.BUFF_SIZE
        numerator = np.sum(rx_phasors * np.conj(loop_phasors), axis=1)
        denominator = np.sum(np.abs(loop_phasors) ** 2, axis=1)
        phasors = numerator / (denominator + 1e-12)

        blocks = np.empty((self.num_retunes, self.num_freqs), dtype=np.complex64)
        if self.costas_mode:
            blocks[np.asarray(self.step_order, dtype=int)] = phasors
        else:
            blocks[:] = phasors
        self.S[:] = blocks.reshape(-1)

        processing_seconds = time.perf_counter() - processing_started
        transfer_seconds = max(0.0, request_seconds - acquisition_seconds)
        self.controller_timings = timings
        self.controller_acquisition_times.append(acquisition_seconds)
        self.controller_transfer_times.append(transfer_seconds)
        self.host_processing_times.append(processing_seconds)
        self.range_profile_times[:] = [request_seconds + processing_seconds]

        if self.verbose:
            self._print_timing_summary(timings)
            print(f"{'PS acquisition':<24} {acquisition_seconds * 1e3:>12.3f} ms")
            print(f"{'SSH transfer/overhead':<24} {transfer_seconds * 1e3:>12.3f} ms")
            print(f"{'Host phasor processing':<24} {processing_seconds * 1e3:>12.3f} ms")
        return self.S

    @staticmethod
    def _duration_stats(seconds):
        values = np.asarray(seconds, dtype=float)
        if values.size == 0:
            return None
        milliseconds = values * 1e3
        return {
            "count": int(values.size),
            "mean_ms": float(np.mean(milliseconds)),
            "median_ms": float(np.median(milliseconds)),
            "p95_ms": float(np.percentile(milliseconds, 95)),
            "p99_ms": float(np.percentile(milliseconds, 99)),
            "max_ms": float(np.max(milliseconds)),
        }

    def benchmark(self, frames=600, warmup_frames=10, deadline_s=0.1, frame_callback=None):
        """Benchmark complete PS-controlled range-profile frames."""
        if not self.use_ps_controller:
            raise RuntimeError("benchmark() requires use_ps_controller=True")
        if not isinstance(frames, int) or frames <= 0:
            raise ValueError("frames must be a positive integer")
        if not isinstance(warmup_frames, int) or warmup_frames < 0:
            raise ValueError("warmup_frames must be a nonnegative integer")
        if not np.isfinite(deadline_s) or deadline_s <= 0:
            raise ValueError("deadline_s must be positive and finite")

        previous_timing_setting = self.collect_controller_timings
        self.collect_controller_timings = True
        end_to_end = []
        acquisitions = []
        transfers = []
        phasor_processing = []
        range_processing = []
        display = []
        operation_frame_totals = {}
        operation_calls = {}

        try:
            for _ in range(warmup_frames):
                self.sweep()
                self.get_range_profile(plot=False, cal=False)

            for _ in range(frames):
                frame_started = time.perf_counter()
                self.sweep()
                profile_started = time.perf_counter()
                range_axis, profile = self.get_range_profile(plot=False, cal=False)
                range_processing.append(time.perf_counter() - profile_started)

                if frame_callback is not None:
                    display_started = time.perf_counter()
                    frame_callback(range_axis, profile)
                    display.append(time.perf_counter() - display_started)

                end_to_end.append(time.perf_counter() - frame_started)
                acquisitions.append(self.controller_acquisition_times[-1])
                transfers.append(self.controller_transfer_times[-1])
                phasor_processing.append(self.host_processing_times[-1])

                per_frame = {}
                for record in self.controller_timings:
                    operation = " ".join(
                        part
                        for part in (record["side"], record["operation"])
                        if part
                    )
                    duration = record["duration_s"]
                    per_frame[operation] = per_frame.get(operation, 0.0) + duration
                    operation_calls.setdefault(operation, []).append(duration)
                for operation, duration in per_frame.items():
                    operation_frame_totals.setdefault(operation, []).append(duration)
        finally:
            self.collect_controller_timings = previous_timing_setting

        total_seconds = float(np.sum(end_to_end))
        return {
            "frames": frames,
            "warmup_frames": warmup_frames,
            "deadline_ms": deadline_s * 1e3,
            "effective_fps": frames / total_seconds,
            "missed_deadlines": int(np.count_nonzero(np.asarray(end_to_end) > deadline_s)),
            "configured_settling_per_frame_ms": (
                self.retune_delay * self.num_retunes * 1e3
            ),
            "metrics": {
                "end_to_end": self._duration_stats(end_to_end),
                "ps_acquisition": self._duration_stats(acquisitions),
                "transfer_overhead": self._duration_stats(transfers),
                "host_phasor_processing": self._duration_stats(phasor_processing),
                "range_profile_processing": self._duration_stats(range_processing),
                "display_callback": self._duration_stats(display),
            },
            "controller_operation_per_frame": {
                operation: self._duration_stats(durations)
                for operation, durations in operation_frame_totals.items()
            },
            "controller_operation_per_call": {
                operation: self._duration_stats(durations)
                for operation, durations in operation_calls.items()
            },
        }

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

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._controller is not None:
            self._controller.close()
            self._controller = None
            return
        for method_name in ("tx_destroy_buffer", "rx_destroy_buffer", "close"):
            method = getattr(self.sdr, method_name, None)
            if method is not None:
                try:
                    method()
                except Exception:
                    pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SFCW radar controller")
    parser.add_argument("--benchmark", action="store_true", help="benchmark PS range-profile acquisition")
    parser.add_argument("--frames", type=int, default=600)
    parser.add_argument("--warmup-frames", type=int, default=10)
    parser.add_argument("--deadline-ms", type=float, default=100.0)
    parser.add_argument("--fmin", type=float, default=1_000_000_000)
    parser.add_argument("--fmax", type=float, default=1_300_000_000)
    parser.add_argument("--sample-rate", type=float, default=20_000_000)
    parser.add_argument("--linear", action="store_true", help="disable Costas block ordering")
    parser.add_argument("--ps-host", default="192.168.2.1")
    parser.add_argument("--ps-cross-compiler")
    parser.add_argument("--json", type=Path, help="also write the report as JSON")
    args = parser.parse_args()

    with SFCWRadar(
        Fmin=args.fmin,
        Fmax=args.fmax,
        Fs=args.sample_rate,
        costas_mode=not args.linear,
        ps_host=args.ps_host,
        ps_cross_compiler=args.ps_cross_compiler,
        verbose=not args.benchmark,
    ) as sfcw:
        if args.benchmark:
            report = sfcw.benchmark(
                frames=args.frames,
                warmup_frames=args.warmup_frames,
                deadline_s=args.deadline_ms / 1e3,
            )
            output = json.dumps(report, indent=2)
            print(output)
            if args.json:
                args.json.write_text(output + "\n", encoding="utf-8")
