from typing import Optional
from std_msgs.msg import String, Bool
from central_manager.enforcers.wait_at_load_enforcer import WaitAtLoadEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS
from central_manager.state_base import RoverState


class AtLoadZoneToLoad(RoverState):
    def __init__(self, node):
        self.node = node

        node.create_subscription(String, "load_over", self.load_over_callback, 10)
        node.create_subscription(
            Bool, "/proximity_sensor/merchandise", self.merchandise_callback, 10
        )
        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.load_over_publisher = node.create_publisher(String, "load_over", 10)
        self.outcome = None
        self.wait_at_load_enforcer = None

    def load_over_callback(self, msg: String):
        self.outcome = "load_over"

    def merchandise_callback(self, msg: Bool):
        if self.wait_at_load_enforcer:
            self.wait_at_load_enforcer.merchandise_callback(msg)

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def on_enter(self, blackboard):
        self.outcome = None
        self.node.get_logger().info("WAIT_AT_LOAD_ZONE state")
        self.wait_at_load_enforcer = WaitAtLoadEnforcer(self.load_over_publisher)
        blackboard[BLACKBOARD_ENFORCERS] = [self.wait_at_load_enforcer]

    def step(self, blackboard) -> Optional[str]:
        return self.outcome
