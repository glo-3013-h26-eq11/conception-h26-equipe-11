import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

IMU_PORT = "/dev/ttyACM1"


class ImuNode(Node):
    def __init__(self, serial_port=None):
        super().__init__("rover_imu_publisher_node", "rover")

        self.publisher = self.create_publisher(String, "/imu/raw", 10)

        
        if serial_port is None:
            self.serial_port = serial.Serial(IMU_PORT, baudrate=115200, timeout=1)
            serial_port.setRTS(False)
            serial_port.setDTR(False)

        self.timer = self.create_timer(0.1, self.read_imu)

    def read_imu(self):
        line = self.serial_port.readline().decode(errors='ignore').strip()

        if line:
            msg = String()
            msg.data = line
            self.publisher.publish(msg)
            self.get_logger().info(f"IMU: {line}")


def main(args=None):
    rclpy.init(args=args)

    node = ImuNode()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()