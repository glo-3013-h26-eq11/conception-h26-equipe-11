from yasmin import State
import rclpy
from std_msgs.msg import String, Float32, Bool, Empty
from central_manager.enforcers.forward_turn_enforcer import ForwardTurnEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS

INTERSECTION_FILTER_PAUSE_TOPIC = "wall_follow/intersection_filter_pause"


class TurningForwardState(State):
    def __init__(self, node):
        super().__init__(outcomes=["turn_over", "back_to_init"])

        node.create_subscription(String, "turn_over", self.turn_over_callback, 10)

        self.turn_over_publisher = node.create_publisher(String, "turn_over", 10)

        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )

        self.intersection_filter_pause_publisher = node.create_publisher(
            Empty, INTERSECTION_FILTER_PAUSE_TOPIC, 10
        )

        self.car_follower_enforcer: CarFollowEnforcer = None

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.node = node

        self.outcome = None
        self.is_executing = False

    def turn_over_callback(self, msg: String):
        if not self.is_executing:
            return

        self.intersection_filter_pause_publisher.publish(Empty())
        self.outcome = "turn_over"

    def distance_to_car_callback(self, msg: Float32):
        if self.is_executing and self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def rover_stop_callback(self, msg: Bool):
        if self.is_executing and not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
        self.outcome = None
        self.is_executing = True

        try:
            self.node.get_logger().info("TURNING_FORWARD state")

            self.car_follower_enforcer = CarFollowEnforcer()

            blackboard[BLACKBOARD_ENFORCERS] = [
                ForwardTurnEnforcer(self.turn_over_publisher),
                self.car_follower_enforcer,
            ]

            while self.outcome is None:
                rclpy.spin_once(self.node, timeout_sec=0.1)

            return self.outcome
        finally:
            self.is_executing = False
            self.car_follower_enforcer = None
