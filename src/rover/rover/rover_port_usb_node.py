import json
import struct

import serial
import rclpy
from std_msgs.msg import Float32MultiArray, String

from web_interface.system_health_node import HealthPingingNode

JETSON_ROVER_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

FRAME_DELIMITER = b"\r\n"
IMU_FLOAT_COUNT = 15
IMU_FRAME_SIZE_BYTES = IMU_FLOAT_COUNT * 4  # 60 bytes


class RoverUsbPortNode(HealthPingingNode):
    def __init__(self, serial_port=None):
        super().__init__("rover_port_usb_node", "rover")

        self.subscription = self.create_subscription(
            String,
            "/rover/port",
            self.listener_json_callback,
            10,
        )

        self.raw_publisher = self.create_publisher(
            String,
            "/rover/serial/raw",
            10,
        )

        self.imu_simple_publisher = self.create_publisher(
            Float32MultiArray,
            "/rover/imu/simple",
            10,
        )

        self.imu_debug_publisher = self.create_publisher(
            String,
            "/rover/imu/debug",
            10,
        )

        if serial_port is None:
            serial_port = serial.Serial(
                JETSON_ROVER_PORT,
                baudrate=BAUDRATE,
                timeout=0.05,
                dsrdtr=None,
            )
            serial_port.setRTS(False)
            serial_port.setDTR(False)

        self.serial_port = serial_port
        self.serial_buffer = bytearray()
        self.frame_count = 0

        self.read_timer = self.create_timer(0.02, self.read_serial_callback)

        self.initialize_rover_feedback()

    def initialize_rover_feedback(self):
        self.send_json_command('{"T":143,"cmd":0}')  # echo off
        self.send_json_command('{"T":131,"cmd":1}')  # continuous feedback on

    def send_json_command(self, command: str):
        self.serial_port.write(command.encode() + b"\n")

    def listener_json_callback(self, msg: String):
        self.serial_port.write(msg.data.encode() + b"\n")

    def read_serial_callback(self):
        try:
            raw_bytes = self.serial_port.read(self.serial_port.in_waiting or 1)

            if not raw_bytes:
                return

            self.serial_buffer.extend(raw_bytes)

            while FRAME_DELIMITER in self.serial_buffer:
                frame_bytes, _, remaining = self.serial_buffer.partition(FRAME_DELIMITER)
                self.serial_buffer = bytearray(remaining)

                if not frame_bytes:
                    continue

                self.publish_raw_frame(frame_bytes)
                self.try_parse_and_publish_imu(frame_bytes)

        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")

    def publish_raw_frame(self, frame_bytes: bytes):
        raw_msg = String()
        raw_msg.data = frame_bytes.hex()
        self.raw_publisher.publish(raw_msg)

    def try_parse_and_publish_imu(self, frame_bytes: bytes):
        frame_len = len(frame_bytes)

        if frame_len ==62:
            payload = frame_bytes[:60]
        elif frame_len == 60:
            payload = frame_bytes
        else:
            self.get_logger().debug(f"Received non-IMU frame of length {frame_len} bytes")
            return

        try:
            values = struct.unpack("<15f", frame_bytes)
        except struct.error as e:
            self.get_logger().warning(f"Failed to unpack IMU frame: {e}")
            return

        self.frame_count += 1

        roll = values[3]
        pitch = values[4]
        heading = values[5]

        accel_x = values[6]
        accel_y = values[7]
        accel_z = values[8]

        gyro_x = values[9]
        gyro_y = values[10]
        gyro_z = values[11]

        mag_x = values[12]
        mag_y = values[13]
        mag_z = values[14]

        simple_msg = Float32MultiArray()
        simple_msg.data = [
            roll,
            pitch,
            heading,
            accel_x,
            accel_y,
            accel_z,
            gyro_x,
            gyro_y,
            gyro_z,
            mag_x,
            mag_y,
            mag_z,
        ]
        self.imu_simple_publisher.publish(simple_msg)

        debug_msg = String()
        debug_msg.data = json.dumps(
            {
                "roll": roll,
                "pitch": pitch,
                "heading": heading,
                "accel_x": accel_x,
                "accel_y": accel_y,
                "accel_z": accel_z,
                "gyro_x": gyro_x,
                "gyro_y": gyro_y,
                "gyro_z": gyro_z,
                "mag_x": mag_x,
                "mag_y": mag_y,
                "mag_z": mag_z,
            }
        )
        self.imu_debug_publisher.publish(debug_msg)

        if self.frame_count % 10 == 0:
            self.get_logger().info(
                f"IMU[{self.frame_count}] "
                f"heading={heading:.2f} deg | "
                f"gyro_z={gyro_z:.4f} | "
                f"accel=({accel_x:.3f}, {accel_y:.3f}, {accel_z:.3f})"
            )

    def stop(self):
        stop_command = '{"T":1,"L":0.0,"R":0.0}'
        self.serial_port.write(stop_command.encode() + b"\n")

    def destroy_node(self):
        try:
            if self.serial_port is not None and self.serial_port.is_open:
                self.serial_port.close()
        except Exception:
            pass

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    rover_port_subscriber = RoverUsbPortNode()

    try:
        rclpy.spin(rover_port_subscriber)
    finally:
        rover_port_subscriber.stop()
        rover_port_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()