from yasmin import State
import rclpy
from std_msgs.msg import String, Float32
from central_manager.enforcers.stop_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer


class WallFollowingState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "current_node",
            ]
        )

        self.node = node

        node.create_subscription(
            String, "current_node", self.at_intersection_callback, 10
        )

        self.outcome = None

    def at_intersection_callback(self, msg: String):
        self.outcome = "current_node"

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("WALL_FOLLOWING_STATE state")

        blackboard["enforcers"] = [StopSignEnforcer(), CarFollowEnforcer()]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
