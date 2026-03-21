import math
import numpy as np
import rclpy
from web_interface.system_health_node import HealthPingingNode
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

THETA_DEG = 60
LOOKAHEAD = 0.8  # m
DESIRED_DISTANCE_FROM_WALL = 0.10  # m
INTEGRAL_WINDOW_SIZE = 20
MIN_FRONT_DISTANCE = 0.5  # m
KP = 1.0
KD = 0.4
KI = 0.05
MAX_STEERING = 0.9  # radians
SPEED = 0.4  # m/s
LIDAR_OFFSET = math.pi / 2
WHEELBASE = 0.1  # m
FRONT_ARC_DEG = 10
CORNER_THRESHOLD = 0.60  # m


def angle_to_distance(theta_rad, lidar_array, angle_min, angle_increment):
    index = int((theta_rad - angle_min) / angle_increment)
    index = max(0, min(index, len(lidar_array) - 1))
    return lidar_array[index]


def is_valid_lidar_scan(scan: float) -> bool:
    return not math.isinf(scan) and not math.isnan(scan) and scan > 0.0


class WallFollowNode(HealthPingingNode):
    def __init__(self):
        super().__init__("wall_follow_node", "lidar")
        self.create_subscription(LaserScan, "/scan", self.lidar_callback, 10)
        self.drive_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.last_time = None
        self.last_steering = 0.0
        self.last_errors_window = np.array([])

    def lidar_callback(self, scan: LaserScan):
        lidar_range_array = scan.ranges
        angle_min = scan.angle_min
        angle_increment = scan.angle_increment

        front_angles = np.arange(-FRONT_ARC_DEG, FRONT_ARC_DEG + 1, 1)

        theta = np.radians(THETA_DEG)
        theta_b = 0.0
        theta_a = theta_b + theta

        a = angle_to_distance(theta_a, lidar_range_array, angle_min, angle_increment)
        b = angle_to_distance(theta_b, lidar_range_array, angle_min, angle_increment)

        if not is_valid_lidar_scan(a) or not is_valid_lidar_scan(b):
            self.get_logger().warn("Invalid lidar scan, repeating last command")
            self.send_control_command(SPEED, self.last_steering)
            return

        alpha = math.atan((a * math.cos(theta) - b) / (a * math.sin(theta)))
        D_t = b * math.cos(alpha)
        D_tp1 = D_t + LOOKAHEAD * math.sin(alpha)

        error = DESIRED_DISTANCE_FROM_WALL - D_tp1

        now = self.get_clock().now().nanoseconds

        self.get_logger().info(
            f"a: {a:.3f}m, b: {b:.3f}m, alpha: {math.degrees(alpha):.1f}deg, D_t: {D_t:.3f}m"
        )

        if self.last_time is None or len(self.last_errors_window) == 0:
            error_diff = 0.0
            error_integral = 0.0
        else:
            dt = (now - self.last_time) * 1e-9
            de = error - self.last_errors_window[-1]
            error_diff = de / dt
            error_diff = max(min(error_diff, 5.0), -5.0)
            error_integral = np.sum(self.last_errors_window) * dt

        steering = error * KP + error_integral * KI + error_diff * KD
        steering = max(-MAX_STEERING, min(MAX_STEERING, steering))

        self.last_steering = steering
        self.last_time = now

        if len(self.last_errors_window) >= INTEGRAL_WINDOW_SIZE:
            self.last_errors_window = np.roll(self.last_errors_window, -1)
            self.last_errors_window[-1] = error
        else:
            self.last_errors_window = np.append(self.last_errors_window, error)

        for deg in front_angles:

            angle_rad = LIDAR_OFFSET + np.radians(deg)
            dist = angle_to_distance(
                angle_rad, lidar_range_array, angle_min, angle_increment
            )

            if (
                is_valid_lidar_scan(a)
                and a < CORNER_THRESHOLD
                and dist <= MIN_FRONT_DISTANCE
            ):
                bias_strength = (CORNER_THRESHOLD - a) / CORNER_THRESHOLD
                corner_steering = MAX_STEERING * bias_strength
                steering = max(steering, corner_steering)
                steering = max(-MAX_STEERING, min(MAX_STEERING, steering))
                self.get_logger().info(
                    f"Right corner at {a:.2f}m, steering: {math.degrees(steering):.1f}deg"
                )

        self.get_logger().info(
            f"error: {error:.3f}, steering: {math.degrees(steering):.1f}deg"
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
