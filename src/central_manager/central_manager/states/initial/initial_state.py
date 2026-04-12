import json

from yasmin import State
from std_msgs.msg import Bool, String, Int16
import rclpy
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)


class InitialState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "system_ready",
            ]
        )

        self.node = node

        node.create_subscription(Bool, "rover/start", self.rover_start_callback, 10)

        node.create_subscription(String, "current_node", self.at_deposit_callback, 10)

        self.home_deposit_zone_pub = self.node.create_publisher(
            Int16, "home_deposit_zone", 10
        )

        self.home_deposit_zone = None

        self.outcome = None

    def rover_start_callback(self, msg):
        if msg.data and self.home_deposit_zone is not None:
            self.outcome = "system_ready"

    def at_deposit_callback(self, msg):
        data = json.loads(msg.data)

        seen_tag = data.get("tag")

        if seen_tag is not None:

            if self.home_deposit_zone != seen_tag:
                self.node.get_logger().info(f"Potential home deposit : {seen_tag}")

            self.home_deposit_zone = seen_tag

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("INITIAL state")

        blackboard[BLACKBOARD_ENFORCERS] = [ImmobileEnforcer()]

        blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = None

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        home_deposit_data = Int16()
        home_deposit_data.data = self.home_deposit_zone
        self.home_deposit_zone_pub.publish(home_deposit_data)
        self.node.get_logger().info(f"Home deposit : {self.home_deposit_zone}")

        return self.outcome
