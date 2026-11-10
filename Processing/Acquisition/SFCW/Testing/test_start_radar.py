import importlib.util
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np
import serial

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location("start_radar", ROOT / "start_radar.py")
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)
sys.path.insert(0, str(launcher.VIEWER.parent))
from SFCW import StreamRangeProfiles


class FakePort:
    def __init__(self):
        self.data = bytearray()
        self.timeout = 0

    @property
    def in_waiting(self):
        return len(self.data)

    def read(self, count):
        result = bytes(self.data[:count])
        del self.data[:count]
        return result

    def reset_input_buffer(self):
        self.data.clear()

    def write(self, data):
        match = re.search(rb"RADAR_DONE_[0-9a-f]+", data)
        if match:
            self.data.extend(b"echoed command\r\n\n" + match[0] + b":0\n# ")
        return len(data)


class USBLauncherTests(unittest.TestCase):
    def test_partial_frames_noise_and_usb_profile_processing(self):
        port = FakePort()
        source = launcher.USBPackets(port, "1400:5")
        receiver = StreamRangeProfiles(fmin=4e9, fmax=4.3e9, spacing=2e6, packet_source=source)
        source.settimeout(.001)
        phasors = np.arange(receiver.num_bins, dtype=np.float32).astype(np.complex64)
        packet = receiver.HEADER.pack(receiver.MAGIC, 0, 7, 0, len(phasors))
        payload = np.empty((len(phasors), 2), dtype="<f4")
        payload[:, 0], payload[:, 1] = phasors.real, phasors.imag
        line = b"IQPH " + (packet + payload.tobytes()).hex().encode() + b"\r\n"
        port.data.extend(b"startup log\nIQPH invalid\n" + line[:50])
        with self.assertRaises(TimeoutError):
            receiver.get_range_profile()
        port.data.extend(line[50:])
        _, profile, sweep = receiver.get_range_profile()
        self.assertEqual(sweep, 7)
        expected = np.fft.ifft((phasors - phasors.mean()) * receiver.window)
        np.testing.assert_allclose(profile, expected, atol=1e-6)

    def test_exit_and_disconnect_are_reported(self):
        port = FakePort()
        source = launcher.USBPackets(port, "1400:5")
        port.data.extend(b"RADAR_EXIT:1\n")
        with self.assertRaises(TimeoutError):
            source.recvfrom(2048)
        self.assertIn("RADAR_EXIT:1", source.error)
        port.read = Mock(side_effect=serial.SerialException("Disconnected"))
        with self.assertRaises(TimeoutError):
            source.recvfrom(2048)
        self.assertEqual(source.error, "Disconnected")

    def test_commands_distinguish_echo_from_completion(self):
        self.assertEqual(launcher.command(FakePort(), "echo hello"), "echoed command")

    def test_upload_checks_hash_before_replacing_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "radar"
            binary.write_bytes(bytes(range(256)))
            with patch.object(launcher, "command") as command:
                launcher.upload(FakePort(), binary)
        encoded, verification = [call.args[1] for call in command.call_args_list]
        self.assertIn("uudecode", encoded)
        self.assertIn("sha256sum", verification)
        self.assertLess(verification.index("sha256sum"), verification.index("mv "))
        self.assertNotIn("mv ", encoded)

    def test_close_interrupts_and_restores_terminal_once(self):
        port = FakePort()
        port.write = Mock(wraps=port.write)
        source = launcher.USBPackets(port, "1400:5")
        with patch.object(launcher, "command") as command:
            source.close()
            source.close()
        port.write.assert_called_once_with(b"\x03")
        command.assert_called_once_with(port, "stty 1400:5", timeout=3)

    def test_no_device_does_not_build(self):
        with patch.object(launcher.list_ports, "comports", return_value=[]), patch.object(
            launcher.subprocess, "run"
        ) as build:
            self.assertEqual(launcher.main(["--rebuild"]), 1)
        build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
