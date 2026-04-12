from yasmin import State
import rclpy
from std_msgs.msg import String, Bool
from central_manager.enforcers.wait_at_load_enforcer import WaitAtLoadEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


class AtLoadZoneToLoad(State):
    def __init__(self, node):
        super().__init__(outcomes=["load_over", "back_to_init"])

        node.create_subscription(String, "load_over", self.load_over_callback, 10)

        node.create_subscription(
            Bool, "/proximity_sensor/merchandise", self.merchandise_callback, 10
        )

        self.load_over_publisher = node.create_publisher(String, "load_over", 10)

        self.outcome = None

        self.wait_at_load_enforcer = None

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.node = node

    def load_over_callback(self, msg: String):
        self.outcome = "load_over"

    def merchandise_callback(self, msg: Bool):
        if self.wait_at_load_enforcer:
            self.wait_at_load_enforcer.merchandise_callback(msg)

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("WAIT_AT_LOAD_ZONE state")

        self.wait_at_load_enforcer = WaitAtLoadEnforcer(self.load_over_publisher)
        blackboard[BLACKBOARD_ENFORCERS] = [self.wait_at_load_enforcer]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
