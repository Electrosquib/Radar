# Rolling AD9361 fastlock capture

`rolling_fastlock_rx.py` captures one RX buffer at every requested frequency
while treating the AD9361's eight RX fastlock slots as a rolling ring.

## Frequency configuration

Edit the constants near the top of `rolling_fastlock_rx.py`, especially:

```python
FREQUENCIES_HZ = [
    *range(70_000_000, 6_000_000_001, 20_000_000),
    6_000_000_000,
]
SAMPLE_RATE_HZ = 30_720_000
RF_BANDWIDTH_HZ = 20_000_000
RX_BUFFER_SAMPLES = 32_768
```

The default sequence contains 298 frequencies. It uses 20 MHz increments from
70 MHz through 5.990 GHz and explicitly adds 6.000 GHz as a final 10 MHz step.
Starting at 70 MHz, 6.000 GHz is not reachable using only 20 MHz steps. Remove
the last entry for a strict 20 MHz grid, or start at 80 MHz to end exactly at
6 GHz using 20 MHz steps.

## Run

The target must run an ADI Linux image with `iiod` and the AD9361 IIO driver.
On the host:

```sh
python3 -m pip install pyadi-iio
python3 scripts/rolling_fastlock_rx.py --dry-run
python3 scripts/rolling_fastlock_rx.py --uri ip:BOARD_IP
```

Each capture is written as a NumPy `.npy` file under
`fastlock_captures/`. `manifest.csv` records frequency, fastlock slot, command
timing, capture timing, and which future profile refilled the departed slot.

## Rolling sequence

1. Normally tune every requested frequency, store its calibration in a hardware
   slot, and read the 16-byte fastlock profile back into host RAM.
2. Load profiles 0 through 7 into hardware slots 0 through 7.
3. Recall slot 0, wait for lock settling, and acquire one DMA buffer.
4. Recall slot 1.
5. The synthesizer no longer depends on slot 0, so replace slot 0 with profile
   8.
6. Repeat. After slot 7 is captured, recall the newly filled slot 0, which now
   contains profile 8.

Profile generation uses normal tuning and is therefore slower than the capture
pass. The fast capture pass uses `fastlock_recall`; it never performs a normal
LO-frequency write.

## Important timing limitation

Fastlock changes synthesizer lock time, but Python, Ethernet, Linux, and one
buffer-at-a-time IIO calls are not deterministic at microsecond scale. This
script is appropriate for ordered frequency captures, not a phase-continuous or
precisely timed hopping waveform. FPGA pin-controlled fastlock plus an HDL DMA
sequencer is required for deterministic hop/capture timing.

## Board boot/programming

The Python file is a host-side program; it is not embedded in the FPGA
bitstream. The recommended target setup is ADI Kuiper Linux on the Zynq carrier
with the boot files for the exact FMCOMMS/carrier pair.

1. Write an ADI Kuiper Linux image to a 16 GB or larger SD card.
2. On the SD card's FAT `BOOT` partition, select the files for
   FMCOMMS2/3 + the exact carrier. For a standard ZC702 this has historically
   been named similar to
   `zynq-zc702-adv7511-ad936x-fmcomms2-3-4/fmcomms2-3`.
3. Copy that target's `BOOT.BIN` and `devicetree.dtb`, plus
   `zynq-common/uImage`, to the root of the `BOOT` partition.
4. With power off, install the FMCOMMS card in the carrier's supported FMC
   connector, insert the SD card, select SD boot, attach UART and Ethernet, and
   power on.
5. At the 115200-8-N-1 UART console, verify that Linux found the radio:

   ```sh
   iio_info -s
   iio_attr -c ad9361-phy RX_LO frequency
   systemctl status iiod
   ip address
   ```

6. From the host, test connectivity and run the script:

   ```sh
   iio_info -u ip:BOARD_IP
   python3 scripts/rolling_fastlock_rx.py --uri ip:BOARD_IP
   ```

Do not copy this repository's existing `system_top.bit` or standalone
`BOOT.bin` to a standard ZC702 without checking the silicon package. The
bundled bitstream reports a target of `xc7z020clg400`, while a standard ZC702
uses a different Zynq package. The bundled standalone application also has
`IIO_SUPPORT` commented out, so it cannot service this host Python script.

For temporary JTAG testing of a *package-compatible* carrier, open Vivado
Hardware Manager, connect to the target, select **Program Device**, and choose
the matching `.bit` file. JTAG programming is volatile and disappears at power
off. Persistent Linux operation should use the matching `BOOT.BIN`,
`devicetree.dtb`, and kernel on the SD card.
