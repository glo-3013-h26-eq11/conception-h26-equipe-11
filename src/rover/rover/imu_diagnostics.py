#!/usr/bin/env python3
"""
IMU Diagnostics - Identify IMU sensor and data format
Run this to capture sample IMU data and determine sensor type
"""

import serial
import sys
import time

IMU_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
SAMPLE_COUNT = 20


def identify_imu():
    """Capture IMU data in binary and try multiple baud rates"""
    baud_rates = [9600, 115200, 230400, 57600]
    
    for baud in baud_rates:
        print(f"\n{'='*80}")
        print(f"Trying {IMU_PORT} at {baud} baud...")
        print(f"{'='*80}\n")
        
        try:
            port = serial.Serial(IMU_PORT, baudrate=baud, timeout=1)
            port.setRTS(False)
            port.setDTR(False)
            time.sleep(0.5)
            port.reset_input_buffer()
            
            print("Capturing 10 samples (HEX + ASCII)...\n")
            binary_data = []
            found_data = False
            
            for i in range(10):
                raw_bytes = port.read(64)
                if raw_bytes:
                    found_data = True
                    binary_data.append(raw_bytes)
                    
                    # Show hex
                    hex_str = ' '.join(f'{b:02x}' for b in raw_bytes[:32])
                    
                    # Show ASCII (with replacement for unprintable)
                    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw_bytes[:32])
                    
                    print(f"[Sample {i+1}]")
                    print(f"  HEX:   {hex_str}")
                    print(f"  ASCII: {ascii_str}\n")
                
                time.sleep(0.1)
            
            if found_data:
                # Analyze the data
                print("=" * 80)
                print("SENSOR TYPE DETECTION:")
                print("=" * 80 + "\n")
                
                first_sample = binary_data[0]
                
                # Check patterns
                detected = False
                
                if b'$VN' in first_sample or b'VNRRG' in first_sample:
                    print("✓ DETECTED: VectorNav format (VN100/VN300)")
                    detected = True
                elif b'MTi' in first_sample:
                    print("✓ DETECTED: XSENS MTi format")
                    detected = True
                elif any(b'\xaa\x55' in chunk or b'\x55\xaa' in chunk for chunk in binary_data):
                    print("✓ DETECTED: BNO055 or similar with sync bytes")
                    detected = True
                elif first_sample[0] in [0x55, 0xAA]:
                    print("✓ DETECTED: Custom binary protocol with sync byte 0x%02x" % first_sample[0])
                    detected = True
                
                if not detected:
                    print("? UNKNOWN binary format")
                
                print("\nCommon IMU protocols:")
                print("  - MPU9250/ICM-20689: Binary I2C/SPI over UART")
                print("  - BNO055: Sync bytes 0xAA 0x55 + data")
                print("  - VectorNav: ASCII $VNRRG or $VNYPR")
                print("  - XSENS: MTi binary protocol")
                
                port.close()
                return True  # Found valid IMU data
            
            port.close()
            
        except FileNotFoundError:
            print(f"✗ Port {IMU_PORT} not found!")
            break
        except serial.SerialException as e:
            print(f"✗ Failed at {baud} baud: {e}\n")
            continue
    
    print("\n" + "="*80)
    print("⚠️  No valid IMU data found on any baud rate.")
    print("\nTroubleshooting:")
    print("  1. Check IMU power and connections")
    print("  2. Try: ls -la /dev/tty*")
    print("  3. Check syslog: dmesg | grep -i usb")
    print("="*80)
    return False


if __name__ == "__main__":
    identify_imu()
