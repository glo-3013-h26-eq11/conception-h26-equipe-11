import json
import math
import time

from typing import Optional
from std_msgs.msg import String, Float32, Bool
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS
from central_manager.state_base import RoverState
from central_manager.transitions_enum import Transition

BASE_TARGET_DEGREES = 56.6


class TurningLeftState(RoverState):
    def __init__(self, node):
        self.node = node

        node.create_subscription(String, Transition.TURN_OVER.value, self.turn_over_callback, 10)

        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )
        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)
        node.create_subscription(String, "/rover/imu/json", self._imu_callback, 10)

        self.car_follower_enforcer = None
        self.outcome = None
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
            self.node.get_logger().info("no gyro_z")
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
            )
            self.outcome = Transition.TURN_OVER.value

    def _is_turn_done(self) -> bool:
        return abs(self.accumulated_degrees) >= BASE_TARGET_DEGREES

    def turn_over_callback(self, msg: String):
        self.outcome = Transition.TURN_OVER.value

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = Transition.BACK_TO_INIT.value

    def on_enter(self, blackboard):
        self.outcome = None
        self.accumulated_degrees = 0.0
        self.last_imu_time = None

        self.car_follower_enforcer = CarFollowEnforcer()
        self.left_turn_enforcer = LeftTurnEnforcer()

        blackboard[BLACKBOARD_ENFORCERS] = [
            self.car_follower_enforcer,
            self.left_turn_enforcer,
        ]

    def step(self, blackboard) -> Optional[str]:
        return self.outcome
