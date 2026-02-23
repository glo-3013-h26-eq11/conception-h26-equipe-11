import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import json

WHEELBASE = 0.15
TRACK_WIDTH = 0.15
MAX_CMD= 1.0


class RoverInterfaceSubscriber(Node):
    def __init__(self):
        super().__init__("rover_interface_subscriber")

        self.subscription = self.create_subscription(
            Twist,
            "/cmd_vel_safe",
            self.listener_command_callback,
            10,
        )

        self.publisher = self.create_publisher(String, "rover_port", 10)

    def listener_command_callback(self, msg):
        linear_x = msg.linear.x

        angular_z = msg.angular.z

        command = {"T":13, "X": linear_x, "Z": angular_z}
        out_msg = String()
        out_msg.data = json.dumps(command)
        self.publisher.publish(out_msg)
        
    
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