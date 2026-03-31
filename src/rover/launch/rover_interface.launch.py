from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare launch arguments
    enable_imu_control = DeclareLaunchArgument(
        'enable_imu_control',
        default_value='true',
        description='Enable IMU-based control improvements'
    )

    return LaunchDescription(
        [
            enable_imu_control,
            Node(
                package="rover",
                executable="rover_interface_node",
                name="rover_interface",
            ),
            Node(
                package="rover", 
                executable="rover_port_usb_node", 
                name="rover_port_usb"
            ),
            Node(
                package="rover",
                executable="imu_controller_node",
                name="imu_controller",
                parameters=[{
                    'enable_imu_control': LaunchConfiguration('enable_imu_control'),
                    'max_accel_x': 3.0,
                    'gyro_yaw_pid_kp': 0.5,
                    'gyro_yaw_pid_kd': 0.1,
                    'accel_smooth_window': 5,
                }]
            ),
        ]
    )
