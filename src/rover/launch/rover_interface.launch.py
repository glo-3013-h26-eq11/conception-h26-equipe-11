from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription(
        [
            Node(
                package="rover",
                executable="rover_interface_node",
                name="rover_interface",
                respawn_delay=2.0,
                respawn=True,
            ),
            Node(
                package="rover",
                executable="rover_port_usb_node",
                name="rover_port_usb",
                respawn_delay=2.0,
                respawn=True,
            ),
        ]
    )
