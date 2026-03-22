from yasmin import State
import rclpy
from std_msgs.msg import String
from central_manager.enforcers.wait_at_deposit_enforcer import WaitAtDepositEnforcer


class AtDepositZoneToDeposit(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "deposit_over",
            ]
        )

        node.create_subscription(String, "deposit_over", self.deposit_over_callback, 10)

        self.deposit_over_publisher = node.create_publisher(String, "deposit_over", 10)

        self.outcome = None

        self.node = node

    def deposit_over_callback(self, msg: String):
        self.outcome = "deposit_over"

    def execute(self, blackboard):
        self.outcome = None

        blackboard["enforcers"] = [WaitAtDepositEnforcer(self.deposit_over_publisher)]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
