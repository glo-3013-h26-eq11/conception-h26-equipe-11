from yasmin import State
import rclpy
from std_msgs.msg import String
from central_manager.enforcers.stop_enforcer import StopEnforcer


class WallFollowingToDepositState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "current_node",
            ]
        )

        node.create_subscription(String, "current_node", self.at_aruco_callback, 10)

        self.outcome = None

    def at_aruco_callback(self, msg: String):
        self.outcome = "current_node"

    def execute(self, blackboard):
        self.outcome = None

        blackboard["enforcers"] = [StopEnforcer()]

        while self.outcome is None:
            rclpy.spin_once(blackboard["node"], timeout_sec=0.1)

        return self.outcome
