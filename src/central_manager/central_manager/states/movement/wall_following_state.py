from yasmin import State
import rclpy
from std_msgs.msg import String, Float32, Bool
import json
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
import time

COOLDOWN_TIME = 2.0


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

        self.car_follower_enforcer: CarFollowEnforcer = None

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.stop_sign_enforcer: StopSignEnforcer = None

        self.outcome = None

        self.cooldown = None

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def at_intersection_callback(self, msg: String):
        data = json.loads(msg.data)
        distance = float(data.get("distance"))

        if self.stop_sign_enforcer:
            self.stop_sign_enforcer.update_distance(distance)

        if self.stop_sign_enforcer:
            if self.stop_sign_enforcer.is_done() and self.is_cooldown_over():
                self.update_cooldown()
                self.outcome = "current_node"

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def update_cooldown(self):
        self.cooldown = time.monotonic()

    def is_cooldown_over(self):
        return self.cooldown is None or time.monotonic() - self.cooldown > COOLDOWN_TIME

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("WALL_FOLLOWING_STATE state")

        self.car_follower_enforcer = CarFollowEnforcer()

        self.stop_sign_enforcer = StopSignEnforcer()

        blackboard["enforcers"] = [self.stop_sign_enforcer, self.car_follower_enforcer]

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
