from yasmin import State
from std_msgs.msg import Bool
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

        self.outcome = None

    def rover_start_callback(self, msg):
        if msg.data:
            self.outcome = "system_ready"

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("INITIAL state")

        blackboard[BLACKBOARD_ENFORCERS] = [ImmobileEnforcer()]

        blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = None

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
