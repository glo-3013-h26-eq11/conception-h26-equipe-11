import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ackermann_msgs.msg import AckermannDriveStamped
import json
import math

WHEELBASE = 0.15
TRACK_WIDTH = 0.15
MAX_CMD= 1.0


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

    def listener_command_callback(self, msg):
        speed = msg.drive.speed
        steering = msg.drive.steering_angle

        left, right = self.ackermann_to_twist(speed, steering)

        command = {
            "T": 1,
            "L": left,
            "R": right,
        }

        out_msg = String()
        out_msg.data = json.dumps(command)
        self.publisher.publish(out_msg)

    def ackermann_to_diff_drive(self, speed, steering_angle):
        if abs(steering_angle) < 0.05:
            left = speed
            right = speed
        else:
            radius = WHEELBASE / math.tan(steering_angle)
            left = speed * (radius - TRACK_WIDTH / 2.0) / radius
            right = speed * (radius + TRACK_WIDTH / 2.0) / radius

        max_mag = max(abs(left), abs(right))
        if max_mag > MAX_CMD:
            left = left / max_mag * MAX_CMD
            right = right / max_mag * MAX_CMD

        return left, right
    
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