import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ackermann_msgs.msg import AckermannDriveStamped
import json


class RoverInterfaceSubscriber(Node):
    def __init__(self):
        super().__init__("rover_interface_subscriber")

        self.subscription = self.create_subscription(
            AckermannDriveStamped,
            "drive",
            self.listener_command_callback,
            10,
        )
        self.publisher = self.create_publisher(String, "rover_port", 10)

    def listener_command_callback(self, msg: AckermannDriveStamped):
        speed = msg.drive.speed
        steering = msg.drive.steering_angle

        command = self.create_movement_dictionary(speed, steering)

        json_msg = json.dumps(command)

        out_msg = String()
        out_msg.data = json_msg

        self.publisher.publish(out_msg)

    def create_movement_dictionary(self, speed, steering):
        return {
            "T": 13,
            "SPEED": speed,
            "STEERING": steering,
        }


def main(args=None):
    rclpy.init(args=args)

    node = RoverInterfaceSubscriber()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()