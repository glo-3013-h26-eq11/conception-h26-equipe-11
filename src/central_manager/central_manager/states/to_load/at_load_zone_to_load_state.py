from yasmin import State
import rclpy
from std_msgs.msg import String
from central_manager.wait_at_load_enforcer import WaitAtLoadEnforcer


class AtLoadZoneToLoad(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "load_over",
            ]
        )

        node.create_subscription(String, "load_over", self.load_over_callback, 10)

        self.outcome = None

    def load_over_callback(self, msg: String):
        self.outcome = "load_over"

    def execute(self, blackboard):
        self.outcome = None

        blackboard["enforcers"] = [WaitAtLoadEnforcer()]

        while self.outcome is None:
            rclpy.spin_once(blackboard["node"], timeout_sec=0.1)

        return self.outcome
