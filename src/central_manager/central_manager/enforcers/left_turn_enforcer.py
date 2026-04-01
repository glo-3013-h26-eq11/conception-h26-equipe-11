import json
import time

from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Node, Publisher
from std_msgs.msg import String
import rclpy
import math

ARC_RADIUS = 0.24  # m
LEFT_TURN_SPEED = 0.4  # m
TARGET_DEGREES = 90


class LeftTurnEnforcer(Enforcer):
    def __init__(self, turn_over_publisher: Publisher):
        super().__init__()

        self.steering_angle_90 = LEFT_TURN_SPEED / ARC_RADIUS
        self.turn_over_publisher = turn_over_publisher

        self.accumulated_degrees = 0.0
        self.last_imu_time = None
        self.turn_finished = False

        # Subscribe to IMU updates. If running in unit tests without ROS node,
        # this may be mocked/monkeypatched by tests.
        self.create_subscription(String, "/rover/imu/json", self.imu_callback, 10)

    def imu_callback(self, msg: String):
        if self.turn_finished:
            return

        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        gyro_z = data.get("gyro_z")
        if gyro_z is None:
            return

        now = time.monotonic()

        if self.last_imu_time is None:
            self.last_imu_time = now
            return

        dt = now - self.last_imu_time
        self.last_imu_time = now

        self.accumulated_degrees += gyro_z * dt

        self.get_logger().info(
            f"Turned: {abs(self.accumulated_degrees):.2f}° / {TARGET_DEGREES}°",
            throttle_duration_sec=0.2,
        )

        if abs(self.accumulated_degrees) >= TARGET_DEGREES:
            self.turn_finished = True
            self.turn_over_publisher.publish(String())

    def update_with_real_speed(self, real_speed_cmd: Twist):
        # IMU turns are handled directly by imu_callback; distance tracking is not required here.
        pass

    def enforce_cmd(self, cmd) -> Twist:
        cmd = Twist()

        if self.turn_finished:
            # stop rotating once 90° reached
            return cmd

        cmd.angular.z = self.steering_angle_90
        cmd.linear.x = LEFT_TURN_SPEED

        return cmd


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
