from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description() -> LaunchDescription:
    lidar_launch = os.path.join(
        get_package_share_directory("lidar"),
        "launch",
        "lidar_system.launch.py",
    )
    camera_launch = os.path.join(
        get_package_share_directory("camera"),
        "launch",
        "oakd_aruco.launch.py",
    )

    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(camera_launch),
                condition=IfCondition(LaunchConfiguration("use_camera")),
                launch_arguments={
                    "start_depthai": LaunchConfiguration("start_depthai"),
                }.items(),
            ),
            Node(
                package="central_manager",
                executable="enforcer_manager_node",
                name="enforcer_manager_node",
                output="screen",
            ),
            Node(
                package="rover",
                executable="rover_interface_node",
                name="rover_interface_node",
                output="screen",
                parameters=[{"input_topic": "/cmd_vel_safe"}],
            ),
            Node(
                package="rover",
                executable="rover_port_usb_node",
                name="rover_port_usb_node",
                output="screen",
                condition=IfCondition(LaunchConfiguration("use_rover_usb")),
            ),
            Node(
                package="central_manager",
                executable="left_turn_enforcer_node",
                name="left_turn_enforcer_node",
                output="screen",
            ),
        ]
    )
