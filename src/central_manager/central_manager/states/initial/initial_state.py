from yasmin import State
from std_msgs.msg import Bool
import rclpy
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer


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

        blackboard["enforcers"].clear()
        blackboard["enforcers"].append(ImmobileEnforcer())

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
