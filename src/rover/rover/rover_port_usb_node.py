import json
import struct
import time

import serial
import rclpy
from std_msgs.msg import Float32MultiArray, String

from web_interface.system_health_node import HealthPingingNode

JETSON_ROVER_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

NUM_FLOATS = 29
FRAME_TOTAL_SIZE = 120


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
                timeout=1,
            )

            time.sleep(1.0)
            serial_port.reset_input_buffer()

        self.serial_port = serial_port

        self.frame_count = 0

        self.read_timer = self.create_timer(0.02, self.read_serial_callback)

    def send_json_command(self, command: str):
        try:
            self.serial_port.write(command.encode() + b"\n")
        except Exception as e:
            self.get_logger().error(f"Write failed: {e}")

    def listener_json_callback(self, msg: String):
        self.send_json_command(msg.data)

    def request_feedback(self):
        try:
            self.serial_port.write(b'{"T":130}\n')
        except Exception as e:
            self.get_logger().error(f"Request failed: {e}")

    def read_serial_callback(self):
        try:
            self.request_feedback()

            data = self.serial_port.read(FRAME_TOTAL_SIZE)

            if len(data) != FRAME_TOTAL_SIZE:
                return

            payload = data[:-4]

            floats = struct.unpack("f" * NUM_FLOATS, payload)

            self.parse_and_publish(floats)

        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")

    def parse_and_publish(self, floats):
        try:
            imu = {
                "gx": floats[2],
                "gy": floats[3],
                "gz": floats[4],
                "ax": floats[5],
                "ay": floats[6],
                "az": floats[7],
                "mx": floats[8],
                "my": floats[9],
                "mz": floats[10],
            }

            simple_msg = Float32MultiArray()
            simple_msg.data = list(imu.values())
            self.imu_simple_publisher.publish(simple_msg)

            json_msg = String()
            json_msg.data = json.dumps({k: round(v, 4) for k, v in imu.items()})
            self.imu_json_publisher.publish(json_msg)

            self.frame_count += 1

            if self.frame_count % 50 == 0:
                self.get_logger().info(
                    f"IMU[{self.frame_count}] "
                    f"gz={imu['gz']:.3f} "
                    f"accel=({imu['ax']:.2f}, {imu['ay']:.2f}, {imu['az']:.2f})"
                )

        except Exception as e:
            self.get_logger().warning(f"Parse failed: {e}")

    def stop(self):
        try:
            self.serial_port.write(b'{"T":1,"L":0.0,"R":0.0}\n')
        except Exception:
            pass

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
