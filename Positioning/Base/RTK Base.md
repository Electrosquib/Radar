# RTK Base Station
This uses the ESP32-C3 (the super mini dev board) with a UM980 GNSS module for the base station. It communicates with the rover (A Raspberry Pi 5) via BLE. 

# ESP32-C3 + UM980 RTCM base MVP

Configures the UM980 as a stationary base and forwards raw binary RTCM to native
USB. No GPS library or network connection is required.

## Wiring

See [GPIO.md](GPIO.md): ESP32 RX20 connects to UM980 TX; ESP32 TX21 connects to
UM980 RX. Connect common ground and use 3.3 V UART logic. Power the UM980 carrier
according to its specifications and attach a GNSS antenna. UART: 115200 baud, 8N1.

Build profile: `esp32-c3-devkitm-1`. Output uses native USB on GPIO18/19, rather
than an external USB-to-UART bridge.

## Run

1. Upload with PlatformIO: `pio run -t upload`.
2. Keep the antenna stationary outdoors with a clear sky view. The UM980 averages
   its position for 60 seconds of suitable fixes; acquisition can add more time.
3. Connect an RTCM-capable application or rover transport to the USB serial port.
   Close any serial monitor first so the application can open the port.

Each ESP32 restart sends `UNLOG` on the connected UM980 port, then
`MODE BASE TIME 60`, then enables output on that same port:

| RTCM message | Content | Interval |
| --- | --- | --- |
| 1006 | Base antenna position | 10 seconds |
| 1033 | Receiver/antenna description | 10 seconds |
| 1074 / 1084 / 1094 / 1124 | GPS / GLONASS / Galileo / BeiDou observations | 1 second |
| 1230 | GLONASS code-phase biases | 10 seconds |

Commands follow the [Unicore N4 reference manual](https://en.unicorecomm.com/uploads/file/Unicore%20Reference%20Commands%20Manual%20For%20N4%20High%20Precision%20Products_V2_EN_R1.14.pdf).
No `SAVECONFIG` or factory reset is sent. Startup command replies are forwarded
as well; the consuming application must synchronize to RTCM frames (preamble
`0xD3`). The firmware adds no text to the stream. A normal text monitor shows
unreadable binary characters, not readable coordinates.

The averaged base position is approximate, not surveyed, and recalculated after
each ESP32 restart. Rover absolute coordinates inherit that position error.
For repeatable surveyed coordinates, replace `MODE BASE TIME 60` with a known
base-position command. Keep the antenna stationary throughout operation.

If no data arrives, check power, common ground, crossed TX/RX, and receiver baud.
Commands are sent once at startup: reset the ESP32 after the UM980 boots if they
were missed. NTRIP/radio transport and RTCM decoding are not included.
