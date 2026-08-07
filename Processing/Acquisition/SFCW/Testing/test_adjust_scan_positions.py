import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np


MODULE_PATH = Path(__file__).resolve().parents[1] / "adjust_scan_positions.py"
SPEC = importlib.util.spec_from_file_location("adjust_scan_positions", MODULE_PATH)
adjust = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adjust)


class AdjustScanPositionsTests(unittest.TestCase):
    def test_preserves_decreasing_direction_and_first_position(self):
        current = np.array([-2.0, -4.0, -6.0])
        actual = adjust.evenly_spaced_positions(current, 1.5)
        np.testing.assert_allclose(actual, [-2.0, -3.5, -5.0])

    def test_updates_metadata_and_npz_together(self):
        with tempfile.TemporaryDirectory() as directory:
            scene = Path(directory)
            metadata_path = scene / "metadata.json"
            profiles_path = scene / "range_profiles.npz"
            metadata = {
                "scene_title": "Fixture",
                "scan_count": 3,
                "scans": [
                    {"scan_index": index, "position_inches": -2.0 * (index + 1),
                     "position_meters": -0.0508 * (index + 1)}
                    for index in range(3)
                ],
            }
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            np.savez(
                profiles_path,
                rail_pos_in=np.array([-2.0, -4.0, -6.0]),
                range_profiles=np.ones((3, 4)),
            )

            result = adjust.main([
                str(scene), "--spacing", "1.5", "--start", "0",
                "--direction", "increasing", "--no-backup",
            ])

            self.assertEqual(result, 0)
            saved = json.loads(metadata_path.read_text(encoding="utf-8"))
            np.testing.assert_allclose(
                [scan["position_inches"] for scan in saved["scans"]],
                [0.0, 1.5, 3.0],
            )
            np.testing.assert_allclose(
                [scan["position_meters"] for scan in saved["scans"]],
                [0.0, 0.0381, 0.0762],
            )
            with np.load(profiles_path) as profiles:
                np.testing.assert_allclose(profiles["rail_pos_in"], [0.0, 1.5, 3.0])
                np.testing.assert_allclose(profiles["range_profiles"], 1.0)

    def test_rejects_mismatched_scan_counts_without_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            scene = Path(directory)
            metadata_path = scene / "metadata.json"
            original = {
                "scans": [
                    {"scan_index": 0, "position_inches": 0.0},
                    {"scan_index": 1, "position_inches": 1.0},
                ]
            }
            metadata_path.write_text(json.dumps(original), encoding="utf-8")
            np.savez(scene / "range_profiles.npz", rail_pos_in=np.array([0.0]))

            result = adjust.main([str(scene), "--spacing", "2"])

            self.assertEqual(result, 2)
            self.assertEqual(
                json.loads(metadata_path.read_text(encoding="utf-8")), original
            )


if __name__ == "__main__":
    unittest.main()
