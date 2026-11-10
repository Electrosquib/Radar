"""Start the PS radar and browser viewer over its USB serial console."""
import argparse
import binascii
import hashlib
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
import uuid

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parent
APPS = ROOT / "Processing" / "Firmware" / "Apps"
VIEWER = ROOT / "Processing" / "Acquisition" / "SFCW" / "StreamingRangeProfileViewer.py"


def command(port, text, timeout=10):
    marker = "RADAR_DONE_" + uuid.uuid4().hex
    port.timeout = 0.05
    port.reset_input_buffer()
    port.write((text + f"\nprintf '\\n{marker}:%s\\n' \"$?\"\n").encode())
    response = bytearray()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response.extend(port.read(max(1, min(port.in_waiting, 8192))))
        match = re.search(rb"\n" + marker.encode() + rb":(\d+)", response)
        if match:
            output = response[:match.start()].decode(errors="replace").strip()
            if int(match[1]):
                raise RuntimeError(output or "PS command failed")
            return output
        if len(response) > 262144:
            raise RuntimeError("Unexpectedly large PS console response")
    raise TimeoutError("PS console did not finish the command")


def login(port):
    port.write(b"\n")
    response = bytearray()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        response.extend(port.read(max(1, min(port.in_waiting, 8192))))
        if response.rstrip().endswith(b"login:"):
            port.write(b"root\n")
            response.clear()
        elif response.rstrip().endswith(b"Password:"):
            port.write(b"analog\n")
            response.clear()
        elif response.rstrip().endswith(b"#"):
            return
        if b"IQPH " in response:
            raise RuntimeError("Radar already running on this console; stop it first")
    raise TimeoutError("Could not log in to the PS USB console")


def upload(port, binary):
    data = binary.read_bytes()
    encoded = "".join(binascii.b2a_uu(data[i:i + 45]).decode() for i in range(0, len(data), 45))
    command(port, "uudecode -o /root/radar.usb-new <<'RADAR_UPLOAD'\n"
            + "begin 700 radar\n" + encoded + chr(96) + "\nend\nRADAR_UPLOAD", timeout=30)
    digest = hashlib.sha256(data).hexdigest()
    command(port, f'test "$(sha256sum /root/radar.usb-new | cut -d " " -f 1)" = "{digest}" '
            "&& chmod 700 /root/radar.usb-new && mv /root/radar.usb-new /root/radar")


class USBPackets:
    def __init__(self, port, terminal_settings):
        self.port = port
        self.terminal_settings = terminal_settings
        self.buffer = bytearray()
        self.timeout = 0.01
        self.error = None
        self.closed = False

    def settimeout(self, timeout):
        self.timeout = timeout
        self.port.timeout = timeout

    def recvfrom(self, size):
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            newline = self.buffer.find(b"\n")
            if newline < 0:
                try:
                    self.buffer.extend(self.port.read(max(1, min(self.port.in_waiting, 4096))))
                except serial.SerialException as error:
                    self.error = str(error)
                    raise TimeoutError from error
                if len(self.buffer) > 16384:
                    self.buffer.clear()
                continue
            line = bytes(self.buffer[:newline]).rstrip(b"\r")
            del self.buffer[:newline + 1]
            if line.startswith(b"RADAR_EXIT:"):
                self.error = "PS radar stopped: " + line.decode(errors="replace")
                raise TimeoutError(self.error)
            if line.startswith(b"IQPH ") and len(line) <= 5 + 1472 * 2:
                try:
                    packet = bytes.fromhex(line[5:].decode("ascii"))
                except (ValueError, UnicodeDecodeError):
                    continue
                if len(packet) <= size:
                    return packet, "USB"
            elif line.startswith(b"[-]"):
                print(line.decode(errors="replace"), flush=True)
        raise TimeoutError("Waiting for USB sweep")

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            self.port.write(b"\x03")
            command(self.port, "stty " + self.terminal_settings, timeout=3)
        except (OSError, RuntimeError) as error:
            print(f"USB cleanup: {error}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Commands (from the repository root):
  python start_radar.py             Start USB capture using the installed radar binary.
  python start_radar.py --rebuild   Compile and upload radar.c, then start USB capture.
  python Processing/Acquisition/SFCW/StreamingRangeProfileViewer.py
                                   Open the UDP viewer only (port 5000).

Connect one PlutoSDR and close other programs using its serial console.
The launcher finds the console, logs in, starts acquisition, and opens the browser.
Rebuild/upload requires make and the ARM compiler configured by the Makefile;
uploads are verified with SHA-256 before replacing the installed binary.

Viewer controls and status:
  Amplitude slider: adjust the trace and waterfall dB limits.
  Terminal output: sweep rate, stability, dropped packets, incomplete sweeps.
  Ctrl+C in this terminal: stop capture and the viewer.
  Closing only the browser tab does not stop capture."""
    )
    parser.add_argument("--rebuild", action="store_true", help="Compile and upload radar.c over USB first")
    args = parser.parse_args(argv)
    try:
        ports = [p.device for p in list_ports.comports() if p.vid == 0x0456 and p.pid == 0xB673]
        if len(ports) != 1:
            raise RuntimeError("Connect one PlutoSDR USB serial console (currently COM3)")
        if args.rebuild:
            subprocess.run(["make", "build"], cwd=APPS, check=True)
        with serial.Serial(ports[0], 115200, timeout=0.05, write_timeout=10) as port:
            login(port)
            matches = re.findall(r"(?m)^([0-9a-f]+(?::[0-9a-f]+)+)\r*$", command(port, "stty -g"))
            if not matches:
                raise RuntimeError("Could not read PS terminal settings")
            settings = matches[-1]
            source = None
            try:
                command(port, "stty -echo -onlcr -ixon -ixoff")
                command(port, "if pidof radar >/dev/null; then echo 'Radar already running; stop it first'; false; fi")
                if args.rebuild:
                    print(f"Uploading radar over {ports[0]}...", flush=True)
                    upload(port, APPS / "radar")
                command(port, "if ! test -x /root/radar || ! grep -q -- '--serial' /root/radar; then "
                        "echo 'Run start_radar.py --rebuild to install the USB sender'; false; fi")

                import matplotlib
                matplotlib.use("WebAgg")
                import matplotlib.pyplot as plt
                import tornado.ioloop

                source = USBPackets(port, settings)
                port.write(b"/root/radar --serial; printf '\\nRADAR_EXIT:%s\\n' \"$?\"\n")
                print(f"Receiving PS sweeps over {ports[0]}. Ctrl+C stops capture and the viewer.", flush=True)

                def check_sender():
                    if source.error:
                        tornado.ioloop.IOLoop.current().stop()

                monitor = tornado.ioloop.PeriodicCallback(check_sender, 500)
                monitor.start()
                sys.path.insert(0, str(VIEWER.parent))
                try:
                    runpy.run_path(str(VIEWER), run_name="__main__", init_globals={"packet_source": source})
                finally:
                    monitor.stop()
                    plt.close("all")
                if source.error:
                    raise RuntimeError(source.error)
            finally:
                if source is not None:
                    source.close()
                else:
                    command(port, "stty " + settings, timeout=3)
        return 0
    except KeyboardInterrupt:
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Startup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
