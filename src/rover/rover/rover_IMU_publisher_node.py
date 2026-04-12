import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32MultiArray
import serial
import threading
import time
from math import sqrt, atan2


class ImuPublisherNode(Node):

    def __init__(self):
        super().__init__("rover_imu_publisher_node")

        self.imu_publisher = self.create_publisher(Imu, "/rover/imu/data", 10)

        self.imu_simple_publisher = self.create_publisher(
            Float32MultiArray, "/rover/imu/simpl7e", 10
        )

        self.get_logger().info(
            "IMU Publisher Node started - Reading from QMI8658 serial port"
        )

        # Serial port variables
        self.serial_port = None
        self.serial_running = True
        self.serial_thread = None

        # IMU data variables
        self.roll_deg = 0.0
        self.pitch_deg = 0.0
        self.yaw_deg = 0.0
        self.temperature = 0.0

        # Processing variables
        self.sample_count = 0
        self.heading_angle = 0.0

        # Start serial reading thread
        self.start_serial_thread()

    def start_serial_thread(self):
        """Start background thread for reading QMI8658 serial data"""
        self.serial_thread = threading.Thread(target=self.serial_read_loop, daemon=True)
        self.serial_thread.start()

    def serial_read_loop(self):
        """Read QMI8658 IMU data from serial port"""
        try:
            self.serial_port = serial.Serial("/dev/ttyACM", 115200, timeout=1)
            self.get_logger().info("Serial port opened successfully")

            while self.serial_running and rclpy.ok():
                try:
                    # Read 4 lines: R:value, P:value, Y:value, T:value
                    roll_line = (
                        self.serial_port.readline()
                        .decode("utf-8", errors="ignore")
                        .strip()
                    )
                    pitch_line = (
                        self.serial_port.readline()
                        .decode("utf-8", errors="ignore")
                        .strip()
                    )
                    yaw_line = (
                        self.serial_port.readline()
                        .decode("utf-8", errors="ignore")
                        .strip()
                    )
                    temp_line = (
                        self.serial_port.readline()
                        .decode("utf-8", errors="ignore")
                        .strip()
                    )

                    if not all([roll_line, pitch_line, yaw_line, temp_line]):
                        continue

                    # Parse values from format "R:value", "P:value", etc
                    if (
                        roll_line.startswith("R:")
                        and pitch_line.startswith("P:")
                        and yaw_line.startswith("Y:")
                        and temp_line.startswith("T:")
                    ):
                        try:
                            self.roll_deg = float(roll_line.split(":")[1])
                            self.pitch_deg = float(pitch_line.split(":")[1])
                            self.yaw_deg = float(yaw_line.split(":")[1])
                            self.temperature = float(temp_line.split(":")[1])

                            # Publish IMU data
                            self.publish_imu_data()
                        except (ValueError, IndexError) as e:
                            self.get_logger().debug(f"Error parsing serial data: {e}")

                except Exception as e:
                    self.get_logger().warn(f"Error reading serial: {e}")
                    rclpy.spin_once(self.node, timeout_sec=0.1)

        except serial.SerialException as e:
            self.get_logger().error(f"Serial port error: {e}")
        finally:
            if self.serial_port:
                self.serial_port.close()
                self.get_logger().info("Serial port closed")

    def publish_imu_data(self):
        """Publish QMI8658 IMU data to ROS2 topics"""
        self.sample_count += 1

        # Convert yaw from degrees to radians for heading angle
        heading_angle_rad = self.yaw_deg * 3.14159 / 180.0

        # Update heading angle (using yaw directly from QMI8658)
        self.heading_angle = heading_angle_rad

        # Create simple message with 9 values
        # [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_accel, mag_gyro, heading_angle]
        simple_msg = Float32MultiArray()
        simple_msg.data = [
            0.0,  # accel_x (not available from serial format)
            0.0,  # accel_y
            0.0,  # accel_z
            0.0,  # gyro_x (not available from serial format)
            0.0,  # gyro_y
            0.0,  # gyro_z
            0.0,  # mag_accel
            0.0,  # mag_gyro
            float(heading_angle_rad),  # heading_angle
        ]
        self.imu_simple_publisher.publish(simple_msg)

        # Log periodically
        if self.sample_count % 10 == 0:
            self.get_logger().info(
                f"QMI8658[{self.sample_count}] - "
                f"Roll: {self.roll_deg:.1f}° | "
                f"Pitch: {self.pitch_deg:.1f}° | "
                f"Yaw: {self.yaw_deg:.1f}° | "
                f"Heading: {heading_angle_rad:.3f} rad ({self.yaw_deg:.1f}°) | "
                f"Temp: {self.temperature:.1f}°C"
            )

    def on_shutdown(self):
        """Cleanup on shutdown"""
        self.serial_running = False
        if self.serial_thread:
            self.serial_thread.join(timeout=2)


def main(args=None):
    rclpy.init(args=args)

    node = ImuPublisherNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.on_shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
