from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Existing launches
    camera_and_aruco_launch = os.path.join(
        get_package_share_directory('camera'),
        'launch', 'oakd_aruco.launch.py'
    )

    lidar_launch = os.path.join(
        get_package_share_directory('lidar'),
        'launch', 'lidar_system.launch.py'
    )

    web_interface_launch = os.path.join(
        get_package_share_directory('web_interface'),
        'launch', 'web_interface_launch.py'
    )

    return LaunchDescription([
        # Camera + Aruco
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(camera_and_aruco_launch)
        ),

        # Lidar
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(lidar_launch)
        ),

        # Web Interface
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(web_interface_launch)
        ),

        # New Launches
        Node(
            package='proximity_sensor',
            executable='proximity_sensor_node',
            name='proximity_sensor'
        ),

        Node(
            package='navigation',
            executable='map_processor_node',
            name='map_processor'
        ),

        Node(
            package='navigation',
            executable='goal_selector_node',
            name='goal_selector'
        ),

        Node(
            package='navigation',
            executable='route_planner',
            name='route_planner'
        ),

        Node(
            package='central_manager',
            executable='enforcer_manager_node',
            name='enforcer_manager'
        ),

        Node(
            package='rover',
            executable='rover_interface_node',
            name='rover_interface'
        ),

        Node(
            package='rover',
            executable='rover_port_usb_node',
            name='rover_port_usb'
        )


    ])
