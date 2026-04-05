import struct
import time

import serial
import rclpy
from std_msgs.msg import Float32MultiArray

from web_interface.system_health_node import HealthPingingNode

JETSON_ROVER_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

NUM_FLOATS = 29
FRAME_SIZE = NUM_FLOATS * 4  # 116 bytes


class RoverUsbPortNode(HealthPingingNode):
    def __init__(self, serial_port=None):
        super().__init__("rover_port_usb_node", "rover")

        self.imu_simple_publisher = self.create_publisher(
            Float32MultiArray,
            "/rover/imu/simple",
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

        self.read_timer = self.create_timer(0.02, self.read_serial_callback)

    def request_feedback(self):
        self.serial_port.write(b'{"T":130}\n')

    def read_serial_callback(self):
        try:
            self.request_feedback()

            data = self.serial_port.read(120)

            if len(data) < 120:
                return

            payload = data[:-4]

            if len(payload) != FRAME_SIZE:
                return

            floats = struct.unpack('f' * NUM_FLOATS, payload)

            self.publish_imu(floats)

        except Exception as e:
            self.get_logger().error(f"Serial error: {e}")

    def publish_imu(self, floats):
        msg = Float32MultiArray()
        msg.data = list(floats)
        self.imu_simple_publisher.publish(msg)

    def destroy_node(self):
        try:
            if self.serial_port.is_open:
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
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()