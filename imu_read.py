"""
WAVE ROVER IMU reader — confirmed 118-byte binary frame format.
Frame structure: \r\n delimited, 118 bytes per frame
  - bytes 0–19:   zeros (5x float32 padding/unused)
  - bytes 20–23:  roll       (degrees)
  - bytes 24–27:  pitch      (degrees)
  - bytes 28–31:  yaw        (degrees)
  - bytes 32–35:  accel_x
  - bytes 36–39:  accel_y
  - bytes 40–43:  accel_z
  - bytes 44–47:  gyro_x
  - bytes 48–51:  gyro_y
  - bytes 52–55:  gyro_z
  - bytes 56–59:  mag_x
  - bytes 60–63:  mag_y
  - bytes 64–67:  mag_z
  - bytes 68–115: additional fields (temp, voltage, etc.)
  - bytes 116–117: trailing 2 bytes (ignored)

Run standalone (no ROS):
    python3 imu_read.py
"""

import struct
import time
import serial

PORT      = "/dev/ttyACM0"
BAUDRATE  = 115200
DELIMITER = b"\r\n"
FRAME_SIZE = 118


def parse_frame(frame: bytes):
    if len(frame) != FRAME_SIZE:
        return None
    try:
        # Unpack 29 floats (116 bytes), ignore trailing 2 bytes
        floats = struct.unpack("<29f", frame[:116])
    except struct.error:
        return None

    return {
        "roll":    round(floats[5],  4),
        "pitch":   round(floats[6],  4),
        "yaw":     round(floats[7],  4),
        "accel_x": round(floats[8],  4),
        "accel_y": round(floats[9],  4),
        "accel_z": round(floats[10], 4),
        "gyro_x":  round(floats[11], 4),
        "gyro_y":  round(floats[12], 4),
        "gyro_z":  round(floats[13], 4),
        "mag_x":   round(floats[14], 4),
        "mag_y":   round(floats[15], 4),
        "mag_z":   round(floats[16], 4),
    }


def main():
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    ser.setRTS(False)
    ser.setDTR(False)
    ser.reset_input_buffer()
    time.sleep(0.3)

    print(f"Reading IMU from {PORT} ...\n")

    buf = bytearray()
    while True:
        chunk = ser.read(ser.in_waiting or 1)
        if not chunk:
            continue

        buf.extend(chunk)

        while DELIMITER in buf:
            frame, _, buf = buf.partition(DELIMITER)

            if len(frame) != FRAME_SIZE:
                if frame:
                    print(f"[skip] unexpected frame size: {len(frame)} bytes")
                continue

            imu = parse_frame(frame)
            if imu:
                print(
                    f"roll={imu['roll']:7.3f}  pitch={imu['pitch']:7.3f}  yaw={imu['yaw']:7.3f}  "
                    f"ax={imu['accel_x']:7.3f}  ay={imu['accel_y']:7.3f}  az={imu['accel_z']:7.3f}"
                )


if __name__ == "__main__":
    main()