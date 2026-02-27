#!/usr/bin/env python3

import launch
import launch_ros.actions
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    ldlidar_launch_dir = os.path.join(
        get_package_share_directory("ldlidar_ros2"), "launch"
    )

    return launch.LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(ldlidar_launch_dir, "stl19p.launch.py")
                )
            ),
            launch_ros.actions.Node(
                package="lidar",
                executable="wall_follower",
                name="wall_follower_node",
                output="screen",
            ),
        ]
    )
