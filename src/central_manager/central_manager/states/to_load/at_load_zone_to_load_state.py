from yasmin import State
import rclpy
from std_msgs.msg import String
from central_manager.enforcers.wait_at_load_enforcer import WaitAtLoadEnforcer


class AtLoadZoneToLoad(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "load_over",
            ]
        )

        node.create_subscription(String, "load_over", self.load_over_callback, 10)

        self.load_over_publisher = node.create_publisher(String, "load_over", 10)

        self.outcome = None

        self.node = node

    def load_over_callback(self, msg: String):
        self.outcome = "load_over"

    def execute(self, blackboard):
        self.outcome = None

        blackboard["enforcers"] = [WaitAtLoadEnforcer(self.load_over_publisher)]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
