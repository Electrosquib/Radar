# ESP32-C3 GPIO assignments

TX and RX below are named from the ESP32's perspective.

| ESP32 pin | Direction | UM980 connection |
| --- | --- | --- |
| GPIO21 (TX) | Output | RX |
| GPIO20 (RX) | Input | TX |
| GND | Common ground | GND |

UART: **115200 baud, 8 data bits, no parity, 1 stop bit**, 3.3 V logic.
Firmware assignments are in `src/main.cpp`.
GPS uses UART1. The monitor uses native USB on GPIO18 (D-) / GPIO19 (D+).
