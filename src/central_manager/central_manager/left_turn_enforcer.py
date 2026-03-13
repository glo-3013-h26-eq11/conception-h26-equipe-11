from central_manager.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Node
import rclpy
import math
import time

ARC_RADIUS = 0.26  # m
LEFT_TURN_SPEED = 0.4  # m

class LeftTurnEnforcer(Enforcer):
    def __init__(self):
        self.last_real_speed_timer = None

        self.steering_angle_90 = LEFT_TURN_SPEED / ARC_RADIUS
        self.travel_distance_90 = 2 * math.pi * ARC_RADIUS
        self.travel_distance_already_done = 0

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

        if self._is_arc_already_done():
            return cmd

        cmd.angular.z = self.steering_angle_90
        cmd.linear.x = LEFT_TURN_SPEED

        return cmd

    def _is_arc_already_done(self) -> bool:
        return self.travel_distance_already_done >= self.travel_distance_90


class LeftTurnNode(Node):
    def __init__(self):
        super().__init__("left_turn_node")

        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)

        self.timer_period = 0.2  # s
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        self.publisher.publish(Twist())


def main(args=None):
    rclpy.init(args=args)

    node = LeftTurnNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
