import launch
import launch_ros.actions
from launch.actions import IncludeLaunchDescription
import os
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    rosbridge_launch = os.path.join(
        get_package_share_directory("rosbridge_server"),
        "launch",
        "rosbridge_websocket_launch.xml",
    )

    return launch.LaunchDescription(
        [
            IncludeLaunchDescription(
                FrontendLaunchDescriptionSource(rosbridge_launch),
                launch_arguments={"port": "9999"}.items(),
            ),
            launch_ros.actions.Node(
                package="web_interface",
                executable="static_web_server",
                name="static_web_server",
            ),
            launch_ros.actions.Node(
                package="web_interface", executable="console_node", name="console_node"
            ),
            launch_ros.actions.Node(
                package="web_interface",
                executable="system_health_node",
                name="system_health_node",
            ),
        ]
    )
