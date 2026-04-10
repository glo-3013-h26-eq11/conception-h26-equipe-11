import json
import math
import time

from yasmin import State
import rclpy
from std_msgs.msg import String, Float32, Bool
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS

BLACKBOARD_ARRIVAL_ALPHA = "arrival_alpha_rad"
BASE_TARGET_DEGREES = 90.0


class TurningLeftState(State):
    def __init__(self, node):
        super().__init__(outcomes=["turn_over", "back_to_init"])

        self.node = node

        node.create_subscription(String, "turn_over", self.turn_over_callback, 10)
        self.turn_over_publisher = node.create_publisher(String, "turn_over", 10)

        node.create_subscription(Float32, "distance_to_car", self.distance_to_car_callback, 10)
        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)
        node.create_subscription(String, "/rover/imu/json", self._imu_callback, 10)

        self.car_follower_enforcer = None
        self.outcome = None

        self.target_degrees = BASE_TARGET_DEGREES
        self.accumulated_degrees = 0.0
        self.last_imu_time = None

    def _imu_callback(self, msg: String):
        if self.outcome is not None:
            return

        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        gyro_z = data.get("gz")
        if gyro_z is None:
            self.node.get_logger().info(f"no gyro_z")
            return

        now = time.monotonic()
        if self.last_imu_time is None:
            self.last_imu_time = now
            return

        dt = now - self.last_imu_time
        self.last_imu_time = now

        self.accumulated_degrees += math.degrees(gyro_z) * dt

        if self._is_turn_done():
            self.node.get_logger().info(
                f"Turn done: accumulated={self.accumulated_degrees:.2f}° "
                f"target={self.target_degrees:.2f}°"
            )
            self.outcome = "turn_over"

    def _is_turn_done(self) -> bool:
        return abs(self.accumulated_degrees) >= abs(self.target_degrees)

    def turn_over_callback(self, msg: String):
        self.outcome = "turn_over"

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
        self.outcome = None
        self.accumulated_degrees = 0.0
        self.last_imu_time = None

        try:
            arrival_alpha_rad = blackboard[BLACKBOARD_ARRIVAL_ALPHA]
        except KeyError:
            arrival_alpha_rad = 0.0

        correction_deg = math.degrees(arrival_alpha_rad)
        self.target_degrees = BASE_TARGET_DEGREES - correction_deg

        self.node.get_logger().info(
            f"TURNING_LEFT state — arrival alpha: {math.degrees(arrival_alpha_rad):.2f}° "
            f"— target turn: {self.target_degrees:.1f}°"
        )

        self.car_follower_enforcer = CarFollowEnforcer()

        blackboard[BLACKBOARD_ENFORCERS] = [
            LeftTurnEnforcer(),
            self.car_follower_enforcer,
        ]

        while self.outcome is None:
            time.sleep(0.1)

        return self.outcome