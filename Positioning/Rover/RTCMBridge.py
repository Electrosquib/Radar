import asyncio
import time

import serial
from bleak import BleakClient, BleakScanner

PORT = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"
BAUD = 115200
SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

async def monitor_nmea(rover):
    buffer = bytearray()
    while True:
        data = rover.read(rover.in_waiting or 1)
        if data:
            buffer.extend(data)
            while b"\n" in buffer:
                line, _, remaining = buffer.partition(b"\n")
                buffer = bytearray(remaining)
                print(line.decode("ascii", errors="replace").strip(), flush=True)
            if len(buffer) > 16384:
                buffer.clear()
        await asyncio.sleep(0.01)

async def bridge(verbose=False):
    device = await BleakScanner.find_device_by_filter(
        lambda _, adv: SERVICE_UUID in [
            uuid.lower() for uuid in adv.service_uuids
        ],
        timeout=30,
    )
    if device is None:
        raise RuntimeError("Base not found")

    queue = asyncio.Queue()
    disconnected = asyncio.Event()

    def receive(_, data):
        queue.put_nowait((time.monotonic(), bytes(data)))
        if verbose:
            print(data.hex(" "), flush=True)

    with serial.Serial(PORT, BAUD, timeout=0, write_timeout=1) as rover:
        rover.write(b"UNLOG\r\n")
        rover.write(b"GPGGA 1\r\n")
        nmea_task = asyncio.create_task(monitor_nmea(rover))
        try:
            async with BleakClient(
                device,
                disconnected_callback=lambda _: disconnected.set(),
            ) as client:
                await client.start_notify(TX_UUID, receive)
                print("Connected. Forwarding RTCM.", flush=True)
                total = 0
                last_report = time.monotonic()
                while not disconnected.is_set():
                    if nmea_task.done():
                        await nmea_task
                    try:
                        received_at, data = await asyncio.wait_for(queue.get(), timeout=1)
                    except asyncio.TimeoutError:
                        continue
                    if time.monotonic() - received_at > 2:
                        raise RuntimeError("UART is falling behind")
                    written = await asyncio.to_thread(rover.write, data)
                    if written != len(data):
                        raise RuntimeError("Incomplete UART write")
                    total += written
                    if time.monotonic() - last_report >= 5:
                        print(f"Forwarded {total} bytes", flush=True)
                        last_report = time.monotonic()
        finally:
            nmea_task.cancel()
            await asyncio.gather(nmea_task, return_exceptions=True)

    raise RuntimeError("BLE disconnected")

async def main(verbose=False):
    while True:
        try:
            await bridge(verbose)
        except Exception as error:
            print(f"{error}. Retrying in 3 seconds.", flush=True)
            await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(main(verbose=False))
    except KeyboardInterrupt:
        pass