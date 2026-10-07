import socket
import struct
import numpy as np
import time

PORT = 5000
HEADER = struct.Struct("!IIIHH")
MAGIC = 0x49514441

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16 * 1024 * 1024)
sock.bind(("0.0.0.0", PORT))

buf = bytearray(2048)
view = memoryview(buf)

last_seq = None
received = 0
dropped = 0
t0 = time.time()

while True:
    n, addr = sock.recvfrom_into(buf)

    magic, seq, sweep, tone, samples = HEADER.unpack_from(buf)

    if magic != MAGIC:
        continue

    if last_seq is not None:
        expected = (last_seq + 1) & 0xffffffff
        if seq != expected:
            dropped += (seq - expected) & 0xffffffff

    last_seq = seq
    received += 1

    raw = np.frombuffer(view[:n], dtype="<i2", offset=HEADER.size)
    iq = raw[0::2] + 1j * raw[1::2]

    now = time.time()

    if now - t0 >= 1:
        total = received + dropped
        loss = 100 * dropped / total if total else 0

        print(f"RX: {received}/s  dropped: {dropped}/s  loss: {loss:.2f}%")

        received = 0
        dropped = 0
        t0 = now