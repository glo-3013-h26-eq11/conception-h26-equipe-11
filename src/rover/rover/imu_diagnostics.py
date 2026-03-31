#!/usr/bin/env python3
"""
IMU Diagnostics - Identify IMU sensor and data format
Run this to capture sample IMU data and determine sensor type
"""

import serial
import sys
import time

IMU_PORT = "/dev/ttyACM1"
BAUD_RATE = 115200
SAMPLE_COUNT = 20


def identify_imu():
    """Capture IMU data and print samples"""
    try:
        print(f"Connecting to IMU at {IMU_PORT} ({BAUD_RATE} baud)...")
        port = serial.Serial(IMU_PORT, baudrate=BAUD_RATE, timeout=1)
        port.setRTS(False)
        port.setDTR(False)
        
        print(f"\n✓ Connected! Capturing {SAMPLE_COUNT} samples...\n")
        print("=" * 80)
        
        for i in range(SAMPLE_COUNT):
            try:
                line = port.readline().decode(errors='ignore').strip()
                if line:
                    print(f"[{i+1}] {line}")
            except Exception as e:
                print(f"[{i+1}] ERROR: {e}")
        
        print("=" * 80)
        print("\n📊 ANALYSIS:")
        print("-" * 80)
        print("\nLook at the data format above and compare:")
        print("\n1. MPU6050/MPU9250 (common hobby sensors):")
        print("   Example: 'accel: -0.05, 0.02, 9.81' or 'AX:1234 AY:5678 AZ:9012'")
        print("\n2. BNO055 (9-DOF IMU chip):")
        print("   Example: 'accel: 0.05 0.02 9.81' with comma/space separation")
        print("\n3. VN100/VN300 (professional grade):")
        print("   Example: '$VNRRG,08,+001.23,+001.45,+009.81*XX' (NMEA format)")
        print("\n4. XSENS (professional motion tracking):")
        print("   Example: Binary or ASCII with MTi format")
        print("\n5. Generic CSV format:")
        print("   Example: 'ax,ay,az,gx,gy,gz' or similar")
        print("\n" + "-" * 80)
        print("\nOnce you identify the format, tell me and I'll create a")
        print("proper IMU driver that integrates with your rover control!")
        
        port.close()
        
    except FileNotFoundError:
        print(f"✗ ERROR: Port {IMU_PORT} not found!")
        print("  Make sure your IMU is connected via USB")
        sys.exit(1)
    except serial.SerialException as e:
        print(f"✗ ERROR: Serial connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    identify_imu()
