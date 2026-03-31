#!/usr/bin/env python3
"""
IMU Controller Node for Wave Rover
Improves rover movement using OAK-D IMU feedback:
- Better turns using gyro feedback
- Smooth acceleration control
- Traction control using accelerometer data
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32
import math
from collections import deque


class IMUControllerNode(Node):
    """Controls rover movement using IMU feedback for better performance"""

    def __init__(self):
        super().__init__('imu_controller_node')

        # Parameters
        self.declare_parameter('enable_imu_control', True)
        self.declare_parameter('max_accel_x', 3.0)  # m/s² - max forward acceleration
        self.declare_parameter('gyro_yaw_pid_kp', 0.5)  # Proportional gain for yaw correction
        self.declare_parameter('gyro_yaw_pid_kd', 0.1)  # Derivative gain
        self.declare_parameter('accel_smooth_window', 5)  # samples for smoothing

        # Get parameters
        self.enable_imu = self.get_parameter('enable_imu_control').value
        self.max_accel_x = self.get_parameter('max_accel_x').value
        self.gyro_kp = self.get_parameter('gyro_yaw_pid_kp').value
        self.gyro_kd = self.get_parameter('gyro_yaw_pid_kd').value
        self.accel_window = self.get_parameter('accel_smooth_window').value

        # QoS profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribers
        self.imu_sub = self.create_subscription(
            Imu, '/oak/imu/data', self.imu_callback, qos_profile)
        
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel_safe', self.cmd_vel_callback, 10)

        # Publishers
        self.cmd_vel_improved_pub = self.create_publisher(
            Twist, '/cmd_vel_improved', 10)
        
        self.debug_pub = self.create_publisher(
            Float32, '/imu_control/accel_forward', 10)

        # State tracking
        self.last_cmd_vel = Twist()
        self.last_gyro_yaw = 0.0
        self.accel_history = deque(maxlen=self.accel_window)
        self.last_imu_time = None

        # PID state for yaw correction
        self.gyro_error_sum = 0.0
        self.last_gyro_error = 0.0

        self.get_logger().info('IMU Controller Node started')
        self.get_logger().info(f'  - IMU Control: {"ENABLED" if self.enable_imu else "DISABLED"}')
        self.get_logger().info(f'  - Max Accel: {self.max_accel_x} m/s²')
        self.get_logger().info(f'  - Gyro Yaw PID Kp: {self.gyro_kp}')
        self.get_logger().info(f'  - Accel History Window: {self.accel_window} samples')

    def imu_callback(self, msg: Imu):
        """Process IMU data for control feedback"""
        if not self.enable_imu:
            return

        try:
            # Extract IMU data
            gyro_yaw = msg.angular_velocity.z  # rad/s - rotation around vertical axis
            accel_x = msg.linear_acceleration.x  # m/s² - forward/backward
            accel_y = msg.linear_acceleration.y  # m/s² - left/right
            accel_z = msg.linear_acceleration.z  # m/s² - up/down

            # Store acceleration for smoothing
            self.accel_history.append(accel_y)

            # Calculate moving average of forward acceleration
            if len(self.accel_history) > 0:
                avg_accel_y = sum(self.accel_history) / len(self.accel_history)
            else:
                avg_accel_y = accel_y

            # Publish debug data
            debug_msg = Float32()
            debug_msg.data = avg_accel_y
            self.debug_pub.publish(debug_msg)

            # Improve the last command based on IMU feedback
            improved_cmd = self._improve_cmd_vel(
                self.last_cmd_vel, gyro_yaw, accel_x, avg_accel_y, accel_z
            )

            # Publish improved command
            self.cmd_vel_improved_pub.publish(improved_cmd)

            self.last_gyro_yaw = gyro_yaw

        except Exception as e:
            self.get_logger().error(f'IMU callback error: {e}')

    def cmd_vel_callback(self, msg: Twist):
        """Store the latest command velocity"""
        self.last_cmd_vel = msg

    def _improve_cmd_vel(self, cmd: Twist, gyro_yaw, accel_x, accel_y, accel_z) -> Twist:
        """
        Improve command velocities based on IMU feedback
        
        Args:
            cmd: Original Twist command
            gyro_yaw: Gyroscope Z (yaw) in rad/s
            accel_x: Forward acceleration in m/s²
            accel_y: Lateral acceleration in m/s²
            accel_z: Vertical acceleration in m/s²
        
        Returns:
            Improved Twist command
        """
        improved = Twist()
        improved.linear.x = cmd.linear.x
        improved.linear.y = cmd.linear.y
        improved.linear.z = cmd.linear.z
        improved.angular.x = cmd.angular.x
        improved.angular.y = cmd.angular.y
        improved.angular.z = cmd.angular.z

        # ===== IMPROVEMENT 1: Better Turns with Gyro Feedback =====
        # If rotating, use gyro to correct the actual rotation rate
        if abs(cmd.angular.z) > 0.01:  # If asking for rotation
            # Calculate rotation error (desired vs actual)
            gyro_error = cmd.angular.z - gyro_yaw
            
            # PID correction
            correction = self.gyro_kp * gyro_error + self.gyro_kd * (gyro_error - self.last_gyro_error)
            self.last_gyro_error = gyro_error
            
            # Apply correction to angular velocity
            improved.angular.z = cmd.angular.z + correction * 0.1

        # ===== IMPROVEMENT 2: Smooth Acceleration Control =====
        # Limit forward acceleration to prevent wheel slip
        if abs(cmd.linear.x) > 0.01:  # If moving forward/backward
            # Calculate acceleration limit based on lateral stability
            # High lateral acceleration = low grip = reduce forward accel
            lateral_accel_magnitude = abs(accel_y)
            
            # If lateral acceleration too high, reduce forward velocity
            if lateral_accel_magnitude > 5.0:  # m/s² threshold
                accel_penalty = max(0.5, 1.0 - (lateral_accel_magnitude - 5.0) / 10.0)
                improved.linear.x = cmd.linear.x * accel_penalty
                self.get_logger().debug(f'Traction control: penalty={accel_penalty:.2f}')
            
            # Smooth velocity changes
            accel_rate = accel_y - (9.81 if accel_z < 0 else 0)  # Remove gravity from Z
            if abs(accel_rate) > self.max_accel_x:
                # Reduce velocity if acceleration too high
                accel_penalty = self.max_accel_x / (abs(accel_rate) + 0.1)
                improved.linear.x = cmd.linear.x * min(1.0, accel_penalty)

        return improved


def main(args=None):
    rclpy.init(args=args)
    node = IMUControllerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
