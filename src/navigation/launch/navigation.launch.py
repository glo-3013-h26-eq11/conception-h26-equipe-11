from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription(
        [
            Node(
                package="navigation",
                executable="map_processor_node",
                name="map_processor",
                respawn_delay=2.0,
                respawn=True,
            ),
            Node(
                package="navigation",
                executable="route_planner_node",
                name="route_planner_node",
                respawn_delay=2.0,
                respawn=True,
            ),
            Node(
                package="navigation",
                executable="current_node_from_aruco_node",
                name="current_node_from_aruco_node",
                respawn_delay=2.0,
                respawn=True,
            ),
        ]
    )
