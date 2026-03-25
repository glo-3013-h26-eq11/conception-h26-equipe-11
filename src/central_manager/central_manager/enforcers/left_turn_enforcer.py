import math
from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Publisher
from std_msgs.msg import String

ARC_RADIUS = 0.24       # m
LEFT_TURN_SPEED = 0.4   # m/s


class LeftTurnEnforcer(Enforcer):
    def __init__(self, turn_over_publisher: Publisher):
        super().__init__()
        self.steering_angle_90 = LEFT_TURN_SPEED / ARC_RADIUS
        self.total_distance_to_travel = 2 * math.pi * ARC_RADIUS / 1.5
        self.travel_distance_already_done = 0.0
        self.turn_over_publisher = turn_over_publisher
        self._published = False  # guard: publish turn_over exactly once
        self._logger = None

    def update_with_real_speed(self, real_speed_cmd: Twist) -> None:
        dt = self._compute_delta_time()
        self.travel_distance_already_done += real_speed_cmd.linear.x * dt

    def enforce_cmd(self, cmd: Twist) -> Twist:
        out = Twist()
        if self._is_arc_already_done():
            if not self._published:
                self.turn_over_publisher.publish(String())
                self._published = True
            if self._logger:
                self._logger.info(f"LeftTurnEnforcer: enforced cmd linear={out.linear.x:.2f}, angular={out.angular.z:.2f}")
            return out  # stop the robot
        out.angular.z = self.steering_angle_90
        out.linear.x = LEFT_TURN_SPEED
        if self._logger:
            self._logger.info(f"LeftTurnEnforcer: enforced cmd linear={out.linear.x:.2f}, angular={out.angular.z:.2f}")
        return out

    def _is_arc_already_done(self) -> bool:
        return self.travel_distance_already_done >= self.total_distance_to_travel