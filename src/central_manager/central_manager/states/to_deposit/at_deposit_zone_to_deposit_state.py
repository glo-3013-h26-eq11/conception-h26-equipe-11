from yasmin import State
import time
import rclpy
from std_msgs.msg import String, Bool
from central_manager.enforcers.wait_at_deposit_enforcer import WaitAtDepositEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


class AtDepositZoneToDeposit(State):
    def __init__(self, node):
        super().__init__(outcomes=["deposit_over", "back_to_init"])

        node.create_subscription(String, "deposit_over", self.deposit_over_callback, 10)

        self.deposit_over_publisher = node.create_publisher(String, "deposit_over", 10)

        node.create_subscription(
            Bool, "/proximity_sensor/merchandise", self.merchandise_callback, 10
        )

        self.outcome = None

        self.wait_at_deposit_enforcer = None

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.node = node

    def deposit_over_callback(self, msg: String):
        self.outcome = "deposit_over"

    def merchandise_callback(self, msg: Bool):
        if self.wait_at_deposit_enforcer:
            self.wait_at_deposit_enforcer.merchandise_callback(msg)

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("WAIT_AT_DEPOSIT_ZONE state")

        self.wait_at_deposit_enforcer = WaitAtDepositEnforcer(
            self.deposit_over_publisher
        )
        blackboard[BLACKBOARD_ENFORCERS] = [self.wait_at_deposit_enforcer]

        while self.outcome is None:
            time.sleep(0.1)

        return self.outcome
