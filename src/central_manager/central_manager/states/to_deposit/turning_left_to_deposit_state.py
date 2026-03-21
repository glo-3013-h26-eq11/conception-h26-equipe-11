from yasmin import State
import rclpy
from std_msgs.msg import String
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from central_manager.enforcers.stop_enforcer import StopEnforcer


class TurningLeftToDepositState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "turn_over",
            ]
        )

        node.create_subscription(String, "turn_over", self.turn_over_callback, 10)

        self.outcome = None

    def turn_over_callback(self, msg: String):
        self.outcome = "turn_over"

    def execute(self, blackboard):
        self.outcome = None

        blackboard["enforcers"] = [LeftTurnEnforcer(), StopEnforcer()]

        while self.outcome is None:
            rclpy.spin_once(blackboard["node"], timeout_sec=0.1)

        return self.outcome
