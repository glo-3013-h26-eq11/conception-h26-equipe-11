import json

from typing import Optional
from std_msgs.msg import Bool, String, Int16
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)
from central_manager.state_base import RoverState
from central_manager.transitions_enum import Transition


class InitialState(RoverState):
    def __init__(self, node):
        self.node = node

        node.create_subscription(Bool, "rover/start", self.rover_start_callback, 10)
        node.create_subscription(String, "current_node", self.at_deposit_callback, 10)

        self.home_deposit_zone_pub = self.node.create_publisher(
            Int16, "home_deposit_zone", 10
        )

        self.home_deposit_zone = None
        self.outcome = None

    def rover_start_callback(self, msg):
        if msg.data:
            self.outcome = Transition.SYSTEM_READY.value

    def at_deposit_callback(self, msg):
        data = json.loads(msg.data)

        seen_tag = data.get("tag")

        if seen_tag is not None and self.home_deposit_zone is None:
            if self.home_deposit_zone != seen_tag:
                self.node.get_logger().info(f"Potential home deposit : {seen_tag}")

            self.home_deposit_zone = seen_tag

    def on_enter(self, blackboard):
        self.outcome = None
        self.node.get_logger().info("INITIAL state")
        blackboard[BLACKBOARD_ENFORCERS] = [ImmobileEnforcer()]
        blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = None

        home_deposit_data = Int16()
        home_deposit_data.data = 0
        self.home_deposit_zone_pub.publish(home_deposit_data)

    def step(self, blackboard) -> Optional[str]:
        if self.outcome is None:
            return None

        if self.home_deposit_zone is None:
            self.node.get_logger().info(
                "Home deposit not set, going back to initial state"
            )
            return Transition.BACK_TO_INIT.value

        home_deposit_data = Int16()
        home_deposit_data.data = self.home_deposit_zone
        self.home_deposit_zone_pub.publish(home_deposit_data)
        self.node.get_logger().info(f"Home deposit : {self.home_deposit_zone}")

        return self.outcome
