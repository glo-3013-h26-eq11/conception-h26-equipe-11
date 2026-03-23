from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Publisher
from std_msgs.msg import String

FORWARD_DISTANCE = 0.6 * 1.5  # m
FORWARD_TURN_SPEED = 0.4  # m/s


class ForwardTurnEnforcer(Enforcer):
    def __init__(self, turn_over_publisher: Publisher):
        super().__init__()

        self.travel_distance_already_done = 0
        self.total_distance_to_travel = FORWARD_DISTANCE

        self.turn_over_publisher = turn_over_publisher

    def update_with_real_speed(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.travel_distance_already_done += real_speed_cmd.linear.x * dt

    def enforce_cmd(self, cmd) -> Twist:
        cmd = Twist()

        if self._is_distance_already_done():
            self.turn_over_publisher.publish(String())
            return cmd

        cmd.angular.z = 0.0
        cmd.linear.x = FORWARD_TURN_SPEED

        return cmd

    def _is_distance_already_done(self) -> bool:
        return self.travel_distance_already_done >= self.total_distance_to_travel
