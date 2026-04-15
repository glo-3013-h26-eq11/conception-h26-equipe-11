from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    camera_and_aruco_launch = os.path.join(
        get_package_share_directory("camera"), "launch", "oakd_aruco.launch.py"
    )

    web_interface_launch = os.path.join(
        get_package_share_directory("web_interface"),
        "launch",
        "web_interface_launch.py",
    )

    rover_interface_launch = os.path.join(
        get_package_share_directory("rover"), "launch", "rover_interface.launch.py"
    )

    navigation_launch = os.path.join(
        get_package_share_directory("navigation"), "launch", "navigation.launch.py"
    )

    lidar_launch = os.path.join(
        get_package_share_directory("lidar"), "launch", "lidar_system.launch.py"
    )

    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(camera_and_aruco_launch)
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(web_interface_launch)
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(rover_interface_launch)
            ),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(lidar_launch)),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(navigation_launch)),
            Node(
                package="proximity_sensor",
                executable="proximity_sensor_node",
                name="proximity_sensor",
                respawn_delay=2.0,
                respawn=True
            ),
            Node(
                package="central_manager",
                executable="enforcer_manager_node",
                name="enforcer_manager",
                respawn_delay=2.0,
                respawn=True
            ),
        ]
    )
