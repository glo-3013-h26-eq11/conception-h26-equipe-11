from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription(
        [
            Node(
                package="rover",
                executable="rover_interface_node",
                name="rover_interface",
            ),
            Node(
                package="rover", executable="rover_port_usb_node", name="rover_port_usb"
            ),
        ]
    )

