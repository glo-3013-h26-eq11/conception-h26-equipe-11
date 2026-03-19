from central_manager.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
import time

FORWARD_DISTANCE = 0.6 * 2  # m
FORWARD_TURN_SPEED = 0.4  # m/s


class ForwardTurnEnforcer(Enforcer):
    def __init__(self):
        self.last_real_speed_timer = None

        self.travel_distance_already_done = 0
        self.total_distance_to_travel = FORWARD_DISTANCE

    def update_real_speed(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.travel_distance_already_done += real_speed_cmd.linear.x * dt

    def _compute_delta_time(self):
        if self.last_real_speed_timer is None:
            self.last_real_speed_timer = time.time()

        now = time.time()

        dt = now - self.last_real_speed_timer

        self.last_real_speed_timer = now

        return dt

    def enforce_cmd(self, cmd) -> Twist:
        cmd = Twist()

        if self._is_distance_already_done():
            return cmd

        cmd.angular.z = 0.0
        cmd.linear.x = FORWARD_TURN_SPEED

        return cmd

    def _is_distance_already_done(self) -> bool:
        return self.travel_distance_already_done >= self.total_distance_to_travel
