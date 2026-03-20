from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription(
        [
            Node(
                package="navigation",
                executable="map_processor_node",
                name="map_processor",
            ),
            Node(
                package="navigation",
                executable="goal_selector_node",
                name="goal_selector",
            ),
            Node(
                package="navigation", executable="route_planner", name="route_planner"
            ),
        ]
    )

