import os
import runpy
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["MPLBACKEND"] = "Agg"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
from SFCW import StreamRangeProfiles


class StreamingViewerTests(unittest.TestCase):
    def test_idle_partial_complete_and_disconnected_stream(self):
        receiver = StreamRangeProfiles(
            host="127.0.0.1", port=0, fmin=4e9, fmax=4.3e9, spacing=2e6
        )
        destination = receiver.sock.getsockname()
        phasors = np.arange(receiver.num_bins, dtype=np.float32).astype(complex)

        def exercise_viewer():
            viewer = sys._getframe(1).f_globals
            viewer["fig"].canvas.draw()
            self.assertEqual(viewer["scan_count"], 0)
            self.assertIn("Waiting", viewer["ax"].get_title())
            times = iter([10.0, 10.5])
            viewer["perf_counter"] = lambda: next(times)
            viewer["amplitude_slider"].set_val((-30, 20))
            self.assertEqual(viewer["ax"].get_ylim(), (-30, 20))
            self.assertEqual(viewer["slow_image"].get_clim(), (-30, 20))

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
                for seq, start, end in [(0, 0, 60), (1, 60, receiver.num_bins)]:
                    payload = np.empty((end - start, 2), dtype="<f4")
                    payload[:, 0] = phasors[start:end].real
                    payload[:, 1] = phasors[start:end].imag
                    packet = receiver.HEADER.pack(receiver.MAGIC, seq, 7, start, end - start)
                    sender.sendto(packet + payload.tobytes(), destination)
                    viewer["update"]()
                    self.assertEqual(viewer["scan_count"], seq)

            expected = np.fft.ifft((phasors - phasors.mean()) * receiver.window)
            np.testing.assert_allclose(viewer["complex_rp_hist"][0], expected, atol=1e-6)
            self.assertEqual(viewer["slow_image"].get_array().shape, (1, receiver.num_bins))
            self.assertNotIn("Waiting", viewer["ax"].get_title())
            title = viewer["ax"].get_title()
            viewer["update"]()
            self.assertEqual(viewer["scan_count"], 1)
            self.assertEqual(title, viewer["ax"].get_title())
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
                packet = receiver.HEADER.pack(receiver.MAGIC, 2, 8, 0, receiver.num_bins)
                payload = np.zeros((receiver.num_bins, 2), dtype="<f4")
                payload[:, 0] = phasors.real * 1000
                sender.sendto(packet + payload.tobytes(), destination)
                viewer["update"]()
            self.assertIn("2.0 Hz", viewer["ax"].get_title())
            self.assertEqual(viewer["ax"].get_ylim(), (-30, 20))
            self.assertEqual(viewer["slow_image"].get_clim(), (-30, 20))

        try:
            with patch("SFCW.StreamRangeProfiles", return_value=receiver), patch.object(
                plt, "show", new=exercise_viewer
            ):
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "StreamingRangeProfileViewer.py"))
            self.assertEqual(receiver.sock.fileno(), -1)
        finally:
            receiver.close()
            plt.close("all")


if __name__ == "__main__":
    unittest.main()
