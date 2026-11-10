"""Exercise streaming without importing unrelated IIO/plotting drivers."""
import ast
from collections import deque
import contextlib
import io
from pathlib import Path
import socket
import struct
import threading
import time
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

source = Path(__file__).resolve().parents[1] / 'SFCW.py'
tree = ast.parse(source.read_text())
node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'StreamRangeProfiles')
namespace = dict(np=np, socket=socket, struct=struct, time=time, threading=threading, deque=deque)
exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
StreamRangeProfiles = namespace['StreamRangeProfiles']


class StreamTimingTests(unittest.TestCase):
    def receiver(self):
        sock = MagicMock()
        sock.getsockopt.return_value = 1024 * 1024
        with patch.object(socket, 'socket', return_value=sock), patch.object(threading, 'Thread'), contextlib.redirect_stdout(io.StringIO()):
            receiver = StreamRangeProfiles(fmin=0, fmax=2, spacing=1, verbose=False)
        self.addCleanup(receiver.close)
        self.assertEqual(receiver.actual_receive_buffer_bytes, 1024 * 1024)
        sock.setsockopt.assert_called_with(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
        return receiver

    def packet(self, seq=0, sweep=2**32+7, start=0, count=3, begin=10**12, end=10**12+25_000_000):
        payload = np.array([1, 2] * count, dtype='<f4').tobytes()
        return StreamRangeProfiles.TIMED_HEADER.pack(
            StreamRangeProfiles.TIMED_MAGIC, seq, sweep, start, count, begin, end) + payload

    def accept(self, receiver, packet):
        receiver._accept_packet(memoryview(packet), 100, 150)

    def test_acquisition_and_receive_timing_are_independent(self):
        receiver = self.receiver()
        with patch.object(time, 'perf_counter_ns', return_value=200):
            self.accept(receiver, self.packet())
        _, _, sweep = receiver.get_range_profile(timeout=0)
        self.assertEqual(sweep, 2**32+7)
        metadata = receiver.last_capture_metadata
        self.assertEqual(metadata['zynq_acquisition_duration_ns'], 25_000_000)
        self.assertEqual(metadata['python_receive_duration_ns'], 100)
        self.assertIn('python_processing_duration_ns', metadata)

    def test_repeated_and_old_ids_are_rejected(self):
        receiver = self.receiver()
        self.accept(receiver, self.packet(seq=0, sweep=9))
        receiver.receive_sweep(timeout=0)
        self.accept(receiver, self.packet(seq=1, sweep=9))
        self.accept(receiver, self.packet(seq=2, sweep=8))
        with self.assertRaises(TimeoutError):
            receiver.receive_sweep(timeout=0)
        self.accept(receiver, self.packet(seq=3, sweep=10))
        self.assertEqual(receiver.receive_sweep(timeout=0)[1], 10)
        self.assertEqual(receiver.stale_packets, 2)
        self.assertEqual(receiver.dropped_packets, 0)

    def test_bounded_queue_returns_newest_sweep(self):
        receiver = self.receiver()
        for i in range(6):
            self.accept(receiver, self.packet(seq=i, sweep=i))
        self.assertEqual(len(receiver._completed), 3)
        self.assertEqual(receiver.receive_sweep(timeout=0)[1], 5)
        self.assertEqual(receiver.discarded_sweeps, 5)

    def test_reused_buffer_does_not_change_queued_sweep(self):
        receiver = self.receiver()
        buffer = bytearray(self.packet())
        self.accept(receiver, buffer)
        buffer[:] = bytes(len(buffer))
        data, _ = receiver.receive_sweep(timeout=0)
        np.testing.assert_array_equal(data, [1+2j] * 3)

    def test_legacy_binary_has_no_acquisition_timing(self):
        receiver = self.receiver()
        packet = StreamRangeProfiles.HEADER.pack(StreamRangeProfiles.MAGIC, 0, 4, 0, 3)
        self.accept(receiver, packet + np.zeros(6, dtype='<f4').tobytes())
        self.assertEqual(receiver.receive_sweep(timeout=0)[1], 4)
        self.assertIsNone(receiver.last_capture_metadata['zynq_acquisition_duration_ns'])

    def test_bad_duplicate_and_inconsistent_packets(self):
        receiver = self.receiver()
        first = self.packet(seq=0, start=0, count=1)
        for packet in [self.packet(end=0), self.packet()[:-1], first, first,
                       self.packet(seq=1, start=1, count=2, begin=1),
                       self.packet(seq=2, start=1, count=2)]:
            self.accept(receiver, packet)
        self.assertEqual(receiver.receive_sweep(timeout=0)[1], 2**32+7)
        self.assertEqual(receiver.dropped_packets, 0)

    def test_incomplete_sweep_and_packet_loss(self):
        receiver = self.receiver()
        self.accept(receiver, self.packet(seq=0, sweep=1, count=1))
        self.accept(receiver, self.packet(seq=2, sweep=2))
        self.assertEqual(receiver.receive_sweep(timeout=0)[1], 2)
        self.assertEqual(receiver.incomplete_sweeps, 1)
        self.assertEqual(receiver.dropped_packets, 1)

    def test_shutdown_unblocks_waiter_and_propagates_receiver_errors(self):
        receiver = self.receiver()
        receiver._receiver_error = OSError('test receive failure')
        with self.assertRaisesRegex(RuntimeError, 'UDP receiver failed'):
            receiver.receive_sweep(timeout=0)
        receiver._receiver_error = None
        receiver.close()
        with self.assertRaisesRegex(RuntimeError, 'closed'):
            receiver.receive_sweep(timeout=0)

    def test_continuous_local_udp_reception_while_consumer_pauses(self):
        receiver = StreamRangeProfiles(host='127.0.0.1', port=0, fmin=0, fmax=2, spacing=1, verbose=False)
        self.addCleanup(receiver.close)
        address = receiver.sock.getsockname()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            for i in range(10):
                sender.sendto(self.packet(seq=i, sweep=i), address)
            # Consumer does no DSP/plotting while the receiver keeps draining UDP.
            deadline = time.perf_counter() + 2
            with receiver._condition:
                while receiver.completed_sweeps < 10:
                    remaining = deadline - time.perf_counter()
                    self.assertGreater(remaining, 0)
                    receiver._condition.wait(remaining)
            self.assertEqual(receiver.receive_sweep(timeout=0)[1], 9)
            self.assertEqual(receiver.completed_sweeps, 10)
            self.assertEqual(receiver.discarded_sweeps, 9)
        receiver.close()
        self.assertFalse(receiver._receiver.is_alive())


if __name__ == '__main__':
    unittest.main()
