import json
import struct
import time

import serial
import rclpy
from std_msgs.msg import Float32MultiArray, String

from web_interface.system_health_node import HealthPingingNode

JETSON_ROVER_PORT = "/dev/ttyACM0"
BAUDRATE = 115200
DELIMITER = b"\r\n"
FRAME_SIZE = 118


class RoverUsbPortNode(HealthPingingNode):
    def __init__(self, serial_port=None):
        super().__init__("rover_port_usb_node", "rover")

        self.subscription = self.create_subscription(
            String,
            "/rover/port",
            self.listener_json_callback,
            10,
        )

        self.imu_simple_publisher = self.create_publisher(
            Float32MultiArray,
            "/rover/imu/simple",
            10,
        )

        self.imu_json_publisher = self.create_publisher(
            String,
            "/rover/imu/json",
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
            serial_port.reset_input_buffer()
            time.sleep(0.3)

        self.serial_port = serial_port
        self.serial_buffer = bytearray()
        self.frame_count = 0

        self.read_timer = self.create_timer(0.02, self.read_serial_callback)

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

            while DELIMITER in self.serial_buffer:
                frame, _, self.serial_buffer = self.serial_buffer.partition(DELIMITER)

                if len(frame) != FRAME_SIZE:
                    continue

                self.parse_and_publish(frame)

        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")

    def parse_and_publish(self, frame: bytes):
        try:
            floats = struct.unpack("<29f", frame[:116])
        except struct.error as e:
            self.get_logger().warning(f"Unpack failed: {e}")
            return

        self.frame_count += 1

        imu = {
            "roll":    floats[5],
            "pitch":   floats[6],
            "yaw":     floats[7],
            "accel_x": floats[8],
            "accel_y": floats[9],
            "accel_z": floats[10],
            "gyro_x":  floats[11],
            "gyro_y":  floats[12],
            "gyro_z":  floats[13],
            "mag_x":   floats[14],
            "mag_y":   floats[15],
            "mag_z":   floats[16],
        }

        simple_msg = Float32MultiArray()
        simple_msg.data = [float(v) for v in imu.values()]
        self.imu_simple_publisher.publish(simple_msg)

        json_msg = String()
        json_msg.data = json.dumps({k: round(v, 4) for k, v in imu.items()})
        self.imu_json_publisher.publish(json_msg)

        if self.frame_count % 50 == 0:
            self.get_logger().info(
                f"IMU[{self.frame_count}] "
                f"roll={imu['roll']:.2f} pitch={imu['pitch']:.2f} yaw={imu['yaw']:.2f} | "
                f"accel=({imu['accel_x']:.2f}, {imu['accel_y']:.2f}, {imu['accel_z']:.2f})"
            )

    def stop(self):
        self.serial_port.write(b'{"T":1,"L":0.0,"R":0.0}\n')

    def destroy_node(self):
        try:
            if self.serial_port is not None and self.serial_port.is_open:
                self.serial_port.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RoverUsbPortNode()
    try:
        rclpy.spin(node)
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()