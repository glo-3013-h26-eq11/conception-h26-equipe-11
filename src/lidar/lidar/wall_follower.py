import math
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

THETA_DEG = 60
LOOKAHEAD = 0.6          # m
DESIRED_DISTANCE_FROM_WALL = 0.1  # m
INTEGRAL_WINDOW_SIZE = 10
MIN_FRONT_DISTANCE = 0.4  # m
KP = 1.2
KD = 0.0
KI = 0.0
MAX_STEERING = 0.8        # radians
SPEED = 0.3               # m/s
LIDAR_OFFSET = math.pi / 2
WHEELBASE = 0.1          # m


def angle_to_distance(theta_rad, lidar_array, angle_min, angle_increment):
    index = int((theta_rad - angle_min) / angle_increment)
    index = max(0, min(index, len(lidar_array) - 1))
    return lidar_array[index]


def is_valid_lidar_scan(scan: float) -> bool:
    return not math.isinf(scan) and not math.isnan(scan) and scan > 0.0


class WallFollowNode(Node):
    def __init__(self):
        super().__init__("wall_follow_node")
        self.create_subscription(LaserScan, "/scan", self.lidar_callback, 10)
        self.drive_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.last_time = None
        self.last_steering = 0.0
        self.last_errors_window = np.array([])

    def lidar_callback(self, scan: LaserScan):
        lidar_range_array = scan.ranges
        angle_min = scan.angle_min
        angle_increment = scan.angle_increment

        front = angle_to_distance(LIDAR_OFFSET, lidar_range_array, angle_min, angle_increment)
        if is_valid_lidar_scan(front) and front < MIN_FRONT_DISTANCE:
            self.get_logger().warn(f"Obstacle at {front:.2f}m, stopping")
            self.send_control_command(0.0, 0.0)
            return

        theta = np.radians(THETA_DEG)
        theta_b = -np.pi / 2.0 + LIDAR_OFFSET
        theta_a = theta_b + theta

        a = angle_to_distance(theta_a, lidar_range_array, angle_min, angle_increment)
        b = angle_to_distance(theta_b, lidar_range_array, angle_min, angle_increment)

        if not is_valid_lidar_scan(a) or not is_valid_lidar_scan(b):
            self.get_logger().warn("Invalid lidar scan, repeating last command")
            self.send_control_command(SPEED, self.last_steering)
            return

        alpha = math.atan2((a * math.cos(theta) - b), (a * math.sin(theta)))
        D_t = b * math.cos(alpha)
        D_tp1 = D_t + LOOKAHEAD * math.sin(alpha)

        error = DESIRED_DISTANCE_FROM_WALL - D_tp1

        now = self.get_clock().now().nanoseconds

        if self.last_time is None or len(self.last_errors_window) == 0:
            error_diff = 0.0
            error_integral = 0.0
        else:
            dt = (now - self.last_time) * 1e-9
            de = error - self.last_errors_window[-1]
            error_diff = de / dt
            error_integral = np.sum(self.last_errors_window) * dt

        steering = -(error * KP + error_integral * KI + error_diff * KD)
        steering = max(-MAX_STEERING, min(MAX_STEERING, steering))

        self.last_steering = steering
        self.last_time = now

        if len(self.last_errors_window) >= INTEGRAL_WINDOW_SIZE:
            self.last_errors_window = np.roll(self.last_errors_window, -1)
            self.last_errors_window[-1] = error
        else:
            self.last_errors_window = np.append(self.last_errors_window, error)

        self.get_logger().info(
            f"a: {a:.3f}m, b: {b:.3f}m, alpha: {math.degrees(alpha):.1f}deg, "
            f"D_t: {D_t:.3f}m, D_tp1: {D_tp1:.3f}m, error: {error:.3f}m, steering: {math.degrees(steering):.1f}deg"
        )

        self.send_control_command(SPEED, steering)

    def send_control_command(self, speed: float, steering: float):
        if abs(steering) < 0.05:
            angular_z = 0.0
        else:
            angular_z = speed * math.tan(steering) / WHEELBASE

        twist = Twist()
        twist.linear.x = speed
        twist.angular.z = angular_z
        self.drive_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = WallFollowNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()