from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Node, Publisher
from std_msgs.msg import String
import rclpy
import math

ARC_RADIUS = 0.24  # m
LEFT_TURN_SPEED = 0.4  # m


class LeftTurnEnforcer(Enforcer):
    def __init__(self, turn_over_publisher: Publisher):
        super().__init__()

        self.steering_angle_90 = LEFT_TURN_SPEED / ARC_RADIUS
        self.total_distance_to_travel = 2 * math.pi * ARC_RADIUS / 1.5
        self.travel_distance_already_done = 0

        self.turn_over_publisher = turn_over_publisher

    def update_with_real_speed(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.travel_distance_already_done += real_speed_cmd.linear.x * dt

    def enforce_cmd(self, cmd) -> Twist:
        cmd = Twist()

        if self._is_arc_already_done():
            self.turn_over_publisher.publish(String())
            return cmd

        cmd.angular.z = self.steering_angle_90
        cmd.linear.x = LEFT_TURN_SPEED

        return cmd

    def _is_arc_already_done(self) -> bool:
        return self.travel_distance_already_done >= self.total_distance_to_travel


class LeftTurnNode(Node):
    def __init__(self):
        super().__init__("left_turn_node")

        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)

        self.start_delay_timer = self.create_timer(
            10.0, self.start_delay_timer_callback
        )

        self.timer_period = 0.2  # s

    def start_delay_timer_callback(self):
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.start_delay_timer.cancel()

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
