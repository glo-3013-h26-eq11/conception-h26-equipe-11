import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

ROVER_COMMAND = {
    "FORWARD_SLOWLY": {"T": 1, "L": 0.1, "R": 0.1},
    "FORWARD": {"T": 1, "L": 0.3, "R": 0.3},
    "EMERGENCY_STOP": {"T": 0},
    "FORWARD_LEFT": {"T": 1, "L": 0.1, "R": 0.3},
    "FORWARD_RIGHT": {"T": 1, "L": 0.3, "R": 0.1},
}


class RoverInterfaceSubscriber(Node):
    def __init__(self):
        super().__init__("rover_interface_subscriber")
        self.subscription = self.create_subscription(
            String, "rover_interface", self.listener_command_callback, 10
        )
        self.publisher = self.create_publisher(String, "rover_port", 10)

    def listener_command_callback(self, msg):
        string_msg = msg.data

        if string_msg not in ROVER_COMMAND:
            raise ValueError("Invalid Rover Command")

        command = ROVER_COMMAND[string_msg]

        json_msg = json.dumps(command)

        out_msg = String()
        out_msg.data = json_msg

        self.publisher.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)

    rover_interface_subscriber = RoverInterfaceSubscriber()

    rclpy.spin(rover_interface_subscriber)

    rover_interface_subscriber.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
