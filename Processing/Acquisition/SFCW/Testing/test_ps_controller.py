import io
import importlib.util
from pathlib import Path
import struct
import tempfile
import time
import unittest
from unittest import mock

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "SFCW.py"
SPEC = importlib.util.spec_from_file_location("sfcw_module", MODULE_PATH)
SFCW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SFCW)


class ChunkedReader:
    def __init__(self, data, chunk_size):
        self.data = bytearray(data)
        self.chunk_size = chunk_size

    def read(self, requested):
        count = min(requested, self.chunk_size, len(self.data))
        result = bytes(self.data[:count])
        del self.data[:count]
        return result


class FakeController:
    def __init__(self, raw):
        self.raw = raw

    def sweep(self):
        return self.raw, [], 0.001


class PSControllerTests(unittest.TestCase):
    def test_read_exact_accepts_partial_reads(self):
        stream = ChunkedReader(b"abcdefgh", 2)
        self.assertEqual(SFCW._PSController._read_exact(stream, 8), b"abcdefgh")

    def test_read_exact_rejects_truncation(self):
        with self.assertRaises(SFCW.PSControllerError):
            SFCW._PSController._read_exact(io.BytesIO(b"short"), 10)

    def test_timing_decode(self):
        payload = struct.pack("<HBBIIiQ", 5, 2, 7, 12, 0, 0, 345_000)
        records, offset = SFCW._PSController.decode_timings(payload, 1)
        self.assertEqual(offset, len(payload))
        self.assertEqual(records[0]["operation"], "Fastlock recall")
        self.assertEqual(records[0]["side"], "TX")
        self.assertEqual(records[0]["slot"], 7)
        self.assertAlmostEqual(records[0]["duration_s"], 345e-6)

    def test_timing_decode_rejects_truncation(self):
        with self.assertRaises(SFCW.PSControllerError):
            SFCW._PSController.decode_timings(b"\0" * 8, 1)

    def test_fresh_local_binary_does_not_build(self):
        with tempfile.TemporaryDirectory() as directory:
            apps = Path(directory)
            (apps / "SFCW.c").write_text("source")
            (apps / "Makefile").write_text("makefile")
            binary = apps / "SFCW"
            binary.write_bytes(b"binary")
            future = time.time() + 2
            binary.touch()
            Path(binary).chmod(0o755)
            # Ensure coarse-resolution filesystems still see the binary as newer.
            import os
            os.utime(binary, (future, future))
            with mock.patch.object(
                SFCW._PSController, "_apps_directory", return_value=apps
            ), mock.patch.object(SFCW.subprocess, "run") as run:
                self.assertEqual(
                    SFCW._PSController._ensure_local_binary(None), binary
                )
                run.assert_not_called()

    def test_stale_binary_without_cross_compiler_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            apps = Path(directory)
            (apps / "SFCW.c").write_text("source")
            (apps / "Makefile").write_text("makefile")
            with mock.patch.object(
                SFCW._PSController, "_apps_directory", return_value=apps
            ), mock.patch.object(SFCW.shutil, "which", return_value=None), mock.patch.dict(
                SFCW.os.environ, {}, clear=True
            ):
                with self.assertRaisesRegex(SFCW.PSControllerError, "cross-compiler"):
                    SFCW._PSController._ensure_local_binary(None)

    def test_sweep_payload_is_reshaped(self):
        raw = np.arange(2 * 3 * 4 * 4, dtype="<i2")
        prefix = SFCW._PSController.SWEEP_PREFIX.pack(2, 3, 4, 2, 0, 2_000_000)
        controller = SFCW._PSController.__new__(SFCW._PSController)
        controller._request = lambda message_type: prefix + raw.tobytes()
        samples, timings, acquisition = controller.sweep()
        self.assertEqual(samples.shape, (2, 3, 4, 4))
        np.testing.assert_array_equal(samples.reshape(-1), raw)
        self.assertEqual(timings, [])
        self.assertEqual(acquisition, 0.002)

    def test_host_processing_and_costas_placement(self):
        retunes, averages, samples = 3, 2, 4
        raw = np.zeros((retunes, averages, samples, 4), dtype=np.int16)
        raw[..., 0] = 100
        raw[..., 1] = 50
        raw[..., 2] = 200
        raw[..., 3] = 100

        radar = SFCW.SFCWRadar.__new__(SFCW.SFCWRadar)
        radar._controller = FakeController(raw)
        radar._controller_signature = None
        radar._ps_config_signature = lambda: None
        radar.bb_mixers = np.ones((1, samples), dtype=np.complex128)
        radar.BUFF_SIZE = samples
        radar.num_retunes = retunes
        radar.num_freqs = 1
        radar.costas_mode = True
        radar.step_order = np.array([2, 0, 1])
        radar.S = np.zeros(retunes, dtype=np.complex64)
        radar.controller_timings = []
        radar.controller_acquisition_times = []
        radar.controller_transfer_times = []
        radar.host_processing_times = []
        radar.range_profile_times = []
        radar.verbose = False

        result = radar._sweep_with_ps_controller()
        np.testing.assert_allclose(result, np.full(retunes, 2 + 0j), rtol=1e-6)
        self.assertEqual(len(radar.controller_acquisition_times), 1)
        self.assertEqual(len(radar.host_processing_times), 1)


if __name__ == "__main__":
    unittest.main()
