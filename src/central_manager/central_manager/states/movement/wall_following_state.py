from yasmin import State
import rclpy
from std_msgs.msg import String, Float32, Bool
import json
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)


class WallFollowingState(State):
    def __init__(self, node):
        super().__init__(outcomes=["current_node", "back_to_init"])

        self.node = node

        node.create_subscription(
            String, "current_node", self.at_intersection_callback, 10
        )

        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )

        node.create_subscription(Bool, "stop_over", self.stop_over, 10)
        
        node.create_subscription(Float32, "/wall_follower/alpha", self.alpha_callback, 10)

        self.stop_over_publisher = node.create_publisher(Bool, "stop_over", 10)

        self.car_follower_enforcer: CarFollowEnforcer = None

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.stop_sign_enforcer: StopSignEnforcer = None

        self.latest_alpha = 0.0

        self.outcome = None

        self.cooldown = None

        self.seen_tag = None

        self.previous_tag = None

        self.blackboard = None

    def alpha_callback(self, msg: Float32):
        self.latest_alpha = msg.data

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def at_intersection_callback(self, msg: String):
        data = json.loads(msg.data)

        distance = float(data.get("distance"))
        angle = float(data.get("angle"))

        self.seen_tag = data.get("tag")

        if self.previous_tag is not None:
            if self.seen_tag == self.previous_tag:
                return

        if self.stop_sign_enforcer:
            self.stop_sign_enforcer.update_distance(distance)
            self.stop_sign_enforcer.update_relative_angle(angle)

    def stop_over(self, msg: Bool):
        self.node.get_logger().info("STOPPED : SAYS WALL FOLLOWER")
        if self.blackboard is not None:
            self.blackboard["arrival_alpha_rad"] = self.latest_alpha
        self.outcome = "current_node"

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
        self.blackboard = blackboard 

        self.outcome = None

        self.previous_tag = blackboard[BLACKBOARD_PREVIOUS_STOP_TAG]

        self.node.get_logger().info("WALL_FOLLOWING_STATE state")

        self.car_follower_enforcer = CarFollowEnforcer()

        self.stop_sign_enforcer = StopSignEnforcer(
            self.stop_over_publisher, logger=self.node.get_logger()
        )

        blackboard[BLACKBOARD_ENFORCERS] = [
            self.stop_sign_enforcer,
            self.car_follower_enforcer,
        ]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = self.seen_tag

        return self.outcome
