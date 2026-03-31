#!/usr/bin/env python3
"""
Identify IMU sensor by reading raw data from serial port
Usage: python3 identify_imu.py
"""
import serial
import time
import sys

def identify_imu():
    """Read raw data from IMU serial port and identify sensor"""
    
    print("🔍 IMU Identification Tool")
    print("=" * 50)
    print("Attempting to read from /dev/ttyACM1...")
    
    try:
        # Try common baud rates
        baud_rates = [9600, 115200, 230400, 57600, 38400]
        
        for baud in baud_rates:
            try:
                print(f"\n📡 Trying baud rate: {baud}")
                ser = serial.Serial('/dev/ttyACM1', baud, timeout=2)
                time.sleep(0.5)
                
                # Read some data
                data = ser.read(1000)
                if data:
                    print(f"✅ SUCCESS! Connected at {baud} baud")
                    print(f"\n📦 Raw Data (first 500 bytes):")
                    print("=" * 50)
                    
                    # Show hex dump
                    hex_data = data[:500].hex()
                    for i in range(0, len(hex_data), 32):
                        print(hex_data[i:i+32])
                    
                    print("\n📝 ASCII representation:")
                    print("=" * 50)
                    try:
                        ascii_data = data[:500].decode('ascii', errors='replace')
                        print(ascii_data)
                    except:
                        print("[Binary data - cannot decode as ASCII]")
                    
                    # Analyze data
                    analyze_data(data[:500])
                    ser.close()
                    return
                    
                ser.close()
            except Exception as e:
                continue
        
        print("\n❌ Failed to read from /dev/ttyACM1")
        print("   Make sure the rover is powered on and IMU is connected")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def analyze_data(data):
    """Analyze data to identify IMU type"""
    print("\n🔬 Data Analysis:")
    print("=" * 50)
    
    # Convert to string for analysis
    data_str = str(data)
    
    # Check for common IMU formats
    if b'MPU' in data or b'mpu' in data.lower():
        print("✓ Likely MPU6050 or MPU9250 (InvenSense)")
    elif b'BMI' in data or b'bmi' in data.lower():
        print("✓ Likely BMI160 or BMI270 (Bosch)")
    elif b'ICM' in data or b'icm' in data.lower():
        print("✓ Likely ICM-20602 or ICM-20690 (InvenSense)")
    elif b'LSM' in data or b'lsm' in data.lower():
        print("✓ Likely LSM6D or LSM9DS1 (STMicroelectronics)")
    elif b'VN' in data or b'vn' in data.lower():
        print("✓ Likely VectorNav (VN-100, VN-300)")
    
    # Look for JSON format
    if b'{' in data and b'}' in data:
        print("✓ Data format: JSON")
        try:
            import json
            json_str = data.decode('utf-8', errors='ignore')
            # Try to extract JSON
            start = json_str.find('{')
            end = json_str.rfind('}') + 1
            if start >= 0 and end > start:
                json_obj = json.loads(json_str[start:end])
                print(f"  Keys: {list(json_obj.keys())}")
        except:
            pass
    
    # Look for CSV format
    if b',' in data:
        print("✓ Data format: likely CSV")
        lines = data.decode('utf-8', errors='ignore').split('\n')
        if lines:
            print(f"  Sample line: {lines[0][:100]}")
    
    # Print data length
    print(f"\n📊 Data statistics:")
    print(f"   Raw bytes received: {len(data)}")
    print(f"   Data rate seems OK: {'Yes' if len(data) > 10 else 'No'}")

if __name__ == '__main__':
    identify_imu()
