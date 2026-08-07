import serial
import time

PORT = "/dev/cu.usbmodem1301"
BAUD = 115200
SERIAL_TIMEOUT = 1.0
STARTUP_DELAY = 2.0

STEP_MOVE_TIME = 2.5 * 70 / 255 + .08
SETTLE_TIME = 0.3
N_STEPS = 10

def rail_function(step_idx, approx_pos_in):
    print(f"Function at step {step_idx}, approx {approx_pos_in:.3f} in")
    time.sleep(1)

def open_serial():
    ser = serial.Serial(PORT, BAUD, timeout=SERIAL_TIMEOUT)
    time.sleep(STARTUP_DELAY)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def send_char(ser, cmd):
    ser.write(cmd.encode("ascii"))
    ser.flush()

def move_one_step(ser):
    send_char(ser, "l")
    time.sleep(STEP_MOVE_TIME)
    send_char(ser, "x")
    time.sleep(SETTLE_TIME)

def main():
    ser = open_serial()

    try:
        for i in range(N_STEPS):
            move_one_step(ser)
            approx_pos_in = -(i + 1) * 1.5
            rail_function(i + 1, approx_pos_in)

    except KeyboardInterrupt:
        send_char(ser, "x")

    finally:
        send_char(ser, "x")
        ser.close()

if __name__ == "__main__":
    main()