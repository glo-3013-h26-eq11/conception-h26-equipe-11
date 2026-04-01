#!/usr/bin/env python3
import struct
from statistics import pstdev

RAW_FRAMES = [
    "b53d2a8d153e7f2524c19a99c9c0cdccb2c1cdccd34240430e3ec1e847bd220821417b005cbc8b5f4f3ccdaaf53a8659eb40d49b1f41c8303a4100000d0a",
    "b53d2a8d153e7f2524c19a9979c00000a8c166e6cf4240430e3ec1e847bd220821417b005cbc8b5f4f3ccdaaf53a8659eb40d49b1f41c8303a4100000d0a",
    "b03d0c22443e1c3924c1cdccacc00000a8c16666d14240430e3ec1e847bd220821417b005cbc8b5f4f3ccdaaf53a8659eb40d49b1f41c8303a4100000d0a",
    "8e3d4c6c353e908724c1cdccacc00000a8c16666d14240430e3ec1e847bd220821417b005cbc8b5f4f3ccdaaf53a8659eb40d49b1f41c8303a4100000d0a",
    "8e3d4c6c353e908724c16666b6c09a99b7c1cd4ccc4240430e3ec1e847bd220821417b005cbc8b5f4f3ccdaaf53a8659eb40d49b1f41c8303a4100000d0a",
    "133d0b85303e7f2524c19a99c9c06666aac133b3ce4240430e3ec1e847bd220821417b005cbc8b5f4f3ccdaaf53a8659eb40d49b1f41c8303a4100000d0a",
]

OFFSET = 2
FLOAT_COUNT = 15


def decode_frame(hex_frame: str, offset: int = OFFSET, float_count: int = FLOAT_COUNT):
    raw = bytes.fromhex(hex_frame)
    payload = raw[offset: offset + float_count * 4]
    values = struct.unpack("<" + "f" * float_count, payload)
    return values


def print_single_frame(values):
    for i, v in enumerate(values):
        print(f"{i:2d}: {v:.6f}")


def print_summary(all_values):
    print("\nRésumé par index")
    print("-" * 40)
    for idx in range(len(all_values[0])):
        col = [frame[idx] for frame in all_values]
        print(
            f"{idx:2d}: min={min(col):9.4f}  max={max(col):9.4f}  std={pstdev(col):9.4f}"
        )


def print_interpreted(values):
    print("\nInterprétation testée")
    print("-" * 40)
    print(f"roll?      : {values[2]:.4f}")
    print(f"pitch?     : {values[3]:.4f}")
    print(f"heading?   : {values[4]:.4f}")
    print(f"accel_x?   : {values[5]:.4f}")
    print(f"accel_y?   : {values[6]:.4f}")
    print(f"accel_z?   : {values[7]:.4f}")
    print(f"gyro_x?    : {values[8]:.4f}")
    print(f"gyro_y?    : {values[9]:.4f}")
    print(f"gyro_z?    : {values[10]:.4f}")
    print(f"mag_x?     : {values[11]:.4f}")
    print(f"mag_y?     : {values[12]:.4f}")
    print(f"mag_z?     : {values[13]:.4f}")
    print(f"extra?     : {values[14]:.4f}")


def main():
    decoded = [decode_frame(frame) for frame in RAW_FRAMES]

    print("Première trame décodée")
    print("-" * 40)
    print_single_frame(decoded[0])

    print_interpreted(decoded[0])
    print_summary(decoded)


if __name__ == "__main__":
    main()