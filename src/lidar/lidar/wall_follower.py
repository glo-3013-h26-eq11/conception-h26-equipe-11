import math
import numpy as np
import rclpy
from web_interface.system_health_node import HealthPingingNode
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

THETA_DEG = 60
LOOKAHEAD = 0.35  # m
DESIRED_DISTANCE_FROM_WALL = 0.15  # m
INTEGRAL_WINDOW_SIZE = 20
KP = 5.0
KD = 0.5
KI = 0.05
MAX_STEERING = 1.1  # radians
SPEED = 0.20  # m/s
WHEELBASE = 0.1  # m

OBTUSE_ANGLE_THRESHOLD = 115  # degrees
AFTER_CORNER_THRESHOLD = 0.40  # m

INTERSECTION_HALF_CONE_ANGLE = 45  # degrees
RIGHT_CORNER_SPEED = 0.1
RIGHT_CORNER_STEERING = 0.8


def angle_to_distance(theta_rad, lidar_array, angle_min, angle_increment):
    index = int((theta_rad - angle_min) / angle_increment)
    index = max(0, min(index, len(lidar_array) - 1))
    return lidar_array[index]


def is_valid_lidar_scan(scan: float) -> bool:
    return not math.isinf(scan) and not math.isnan(scan) and scan > 0.0


class WallFollowNode(HealthPingingNode):
    def __init__(self):
        super().__init__("wall_follow_node", "lidar")
        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("output_topic", "/cmd_vel")

        scan_topic = self.get_parameter("scan_topic").value
        output_topic = self.get_parameter("output_topic").value

        self.create_subscription(LaserScan, scan_topic, self.lidar_callback, 10)
        self.drive_pub = self.create_publisher(Twist, output_topic, 10)
        self.last_time = None
        self.last_steering = 0.0
        self.last_speed = 0.0
        self.last_errors_window = np.array([])
        self._corner_detected = False
        self._corner_time = None

    def lidar_callback(self, scan: LaserScan):
        lidar_range_array = scan.ranges
        angle_min = scan.angle_min
        angle_increment = scan.angle_increment
        speed = SPEED

        theta = np.radians(THETA_DEG)
        theta_b = 0.0
        theta_a = theta_b + theta
        theta_front = np.radians(90)

        THETA_C = np.radians(37)

        theta_c = THETA_C

        a = angle_to_distance(theta_a, lidar_range_array, angle_min, angle_increment)
        b = angle_to_distance(theta_b, lidar_range_array, angle_min, angle_increment)
        c = angle_to_distance(theta_c, lidar_range_array, angle_min, angle_increment)

        if (
            not is_valid_lidar_scan(a)
            or not is_valid_lidar_scan(b)
            or not is_valid_lidar_scan(c)
        ):
            self.get_logger().warn("Invalid lidar scan, repeating last command")
            self.send_control_command(self.last_speed, self.last_steering)
            return

        A_a = self.get_A_angle_deg(a, b, theta)
        A_c = self.get_A_angle_deg(c, b, theta_c)

        a_for_wall_follow = a
        theta_for_wall_follow = theta

        front = angle_to_distance(
            theta_front, lidar_range_array, angle_min, angle_increment
        )

        if A_c > A_a:
            theta_for_wall_follow = theta_c
            a_for_wall_follow = c

        if front < 0.25:
            theta_for_wall_follow = theta_front
            a_for_wall_follow = front

        alpha = math.atan(
            (a_for_wall_follow * math.cos(theta_for_wall_follow) - b)
            / (a_for_wall_follow * math.sin(theta_for_wall_follow))
        )
        D_t = b * math.cos(alpha)
        D_tp1 = D_t + LOOKAHEAD * math.sin(alpha)

        error = DESIRED_DISTANCE_FROM_WALL - D_tp1

        error_integral, error_diff = self.update_pid_and_get_error_integral_diff(
            error, self.last_steering
        )

        steering = error * KP + error_integral * KI + error_diff * KD
        steering = max(-MAX_STEERING, min(MAX_STEERING, steering))

        speed, steering = self.filter_intersections(
            a, b, theta, speed, steering, scan, logger=self.get_logger()
        )

        self.send_control_command(speed, steering)

    def update_pid_and_get_error_integral_diff(self, error, steering):
        now = self.get_clock().now().nanoseconds

        if self.last_time is None or len(self.last_errors_window) == 0:
            error_diff = 0.0
            error_integral = 0.0
        else:
            dt = (now - self.last_time) * 1e-9
            de = error - self.last_errors_window[-1]
            error_diff = de / dt
            error_diff = max(min(error_diff, 5.0), -5.0)
            error_integral = np.sum(self.last_errors_window) * dt

        self.last_steering = steering
        self.last_time = now

        if len(self.last_errors_window) >= INTEGRAL_WINDOW_SIZE:
            self.last_errors_window = np.roll(self.last_errors_window, -1)
            self.last_errors_window[-1] = error
        else:
            self.last_errors_window = np.append(self.last_errors_window, error)

        return error_integral, error_diff

    def send_control_command(self, speed: float, steering: float):

        angular_z = speed * math.tan(steering) / WHEELBASE

        self.last_speed = speed
        self.last_steering = steering

        twist = Twist()
        twist.linear.x = speed
        twist.angular.z = angular_z
        self.drive_pub.publish(twist)

    def get_A_angle_deg(self, a, b, theta):
        c = math.sqrt(a**2 + b**2 - (2 * a * b * math.cos(theta)))

        A_rad = math.acos((b**2 + c**2 - a**2) / (2 * b * c))

        A = math.degrees(A_rad)

        return A

    def filter_intersections(
        self, a, b, theta, initial_speed, initial_steering, scan: LaserScan, logger=None
    ):

        b, b_angle_deg = self.get_closest_point_in_half_cone(
            scan, 10, INTERSECTION_HALF_CONE_ANGLE
        )

        A = self.get_A_angle_deg(a, b, theta - math.radians(b_angle_deg))

        if b > AFTER_CORNER_THRESHOLD:

            return RIGHT_CORNER_SPEED, -RIGHT_CORNER_STEERING

        elif A > OBTUSE_ANGLE_THRESHOLD and b < 0.20:

            return RIGHT_CORNER_SPEED, 0

        return initial_speed, initial_steering

    def get_closest_point_in_half_cone(
        self, scan: LaserScan, angle_start_deg, half_cone_angle_deg
    ):
        angles_deg = list(range(angle_start_deg, half_cone_angle_deg))

        min = math.inf
        min_angle = 0

        for angle_deg in angles_deg:
            angle_rad = math.radians(angle_deg)

            distance = angle_to_distance(
                angle_rad, scan.ranges, scan.angle_min, scan.angle_increment
            )

            if not math.isfinite(distance):
                continue

            if distance < min:
                min = distance
                min_angle = angle_deg

        return min, min_angle


def main(args=None):
    rclpy.init(args=args)
    node = WallFollowNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
