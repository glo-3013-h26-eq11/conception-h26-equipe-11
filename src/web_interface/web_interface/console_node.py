import rclpy
from rcl_interfaces.msg import Log
from std_msgs.msg import String
from collections import deque
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from web_interface.system_health_node import HealthPingingNode
import os

LEVEL_NAMES = {10: "DEBUG", 20: "INFO", 30: "WARN", 40: "ERROR", 50: "FATAL"}

MESSAGES_STACK_SIZE = 100

FILTERS = ["rosbridge", "wall_follower_node", "rover_interface"]


class ConsoleNode(HealthPingingNode):
    def __init__(self, message_stack_size=MESSAGES_STACK_SIZE, filters=FILTERS):
        super().__init__("console_node", "web_interface")

        self.subscription = self.create_subscription(
            Log, "rosout", self.log_callback, 10
        )

        self.publisher = self.create_publisher(String, "/console", 10)

        self.messages_stack = deque(maxlen=message_stack_size)

        self.filters = filters

    def log_callback(self, log: Log):

        entry = (
            f"[{self.format_log_stamp_et(log)}] -- "
            f"[{LEVEL_NAMES.get(log.level)}] -- "
            f"{os.path.basename(log.file)} -- "
            f"[{log.name}] -- "
            f"{log.msg}"
        )

        if self.filter_ignore_log(entry):
            return

        self.messages_stack.append(entry)

        msg = String()
        msg.data = json.dumps(list(self.messages_stack))

        self.publisher.publish(msg)

    def format_log_stamp_et(self, log: Log):
        t = log.stamp.sec + log.stamp.nanosec / 1e9
        dt_utc = datetime.fromtimestamp(t)
        dt_et = dt_utc.astimezone(ZoneInfo("America/New_York"))
        return dt_et.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def filter_ignore_log(self, log: str) -> bool:
        for filter in self.filters:
            if filter in log:
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
