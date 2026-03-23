from yasmin import State
import rclpy
from std_msgs.msg import String, Float32
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer


class TurningLeftState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "turn_over",
            ]
        )

        self.node = node

        node.create_subscription(String, "turn_over", self.turn_over_callback, 10)

        self.turn_over_publisher = node.create_publisher(String, "turn_over", 10)

        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )

        self.car_follower_enforcer: CarFollowEnforcer = None

        self.outcome = None

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def turn_over_callback(self, msg: String):
        self.outcome = "turn_over"

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("TURNING_LEFT state")

        self.car_follower_enforcer = CarFollowEnforcer()

        blackboard["enforcers"] = [
            LeftTurnEnforcer(self.turn_over_publisher),
            self.car_follower_enforcer,
            StopSignEnforcer(),
        ]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
