import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import json


class RoverInterfaceNode(Node):
    def __init__(self):
        super().__init__("rover_interface_node")
        self.subscription = self.create_subscription(
            Twist, "/cmd_vel", self.listener_command_callback, 10
        )
        self.publisher = self.create_publisher(String, "/rover/port", 10)

    def listener_command_callback(self, msg):
        linear_x = msg.linear.x

        angular_z = msg.angular.z

        command = self.create_movement_dictionnary(linear_x, angular_z)

        json_msg = json.dumps(command)

        out_msg = String()
        out_msg.data = json_msg

        self.publisher.publish(out_msg)

    def create_movement_dictionnary(self, x, z):
        return {"T": 13, "X": x, "Z": z}


def main(args=None):
    rclpy.init(args=args)

    rover_interface_subscriber = RoverInterfaceNode()
    try:
        rclpy.spin(rover_interface_subscriber)
    finally:
        rover_interface_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
