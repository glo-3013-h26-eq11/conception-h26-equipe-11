import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log
from std_msgs.msg import String

LEVEL_NAMES = {10: "DEBUG", 20: "INFO", 30: "WARN", 40: "ERROR", 50: "FATAL"}


class ConsoleNode(Node):
    def __init__(self):
        super().__init__("console_node")

        self.subscription = self.create_subscription(
            Log, "rosout", self.log_callback, 10
        )

        self.publisher = self.create_publisher(String, "/console", 10)

    def log_callback(self, log: Log):
        if self.filter_ignore_log(log):
            return

        msg = String()
        msg.data = (
            f"[{LEVEL_NAMES.get(log.level)}] -- {log.file} -- [{log.name}] -- {log.msg}"
        )
        self.publisher.publish(msg)

    def filter_ignore_log(self, log: Log) -> bool:
        if "rosbridge" in log.file:
            return True

        return False


def main(args=None):
    rclpy.init(args=args)

    console_node = ConsoleNode()

    try:
        rclpy.spin(console_node)
    finally:
        console_node.stop()

        console_node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()
