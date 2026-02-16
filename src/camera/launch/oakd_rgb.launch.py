from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument("width", default_value="1280"),
            DeclareLaunchArgument("height", default_value="720"),
            DeclareLaunchArgument("fps", default_value="10"),
            DeclareLaunchArgument("publish_compressed", default_value="true"),
            DeclareLaunchArgument("jpeg_quality", default_value="80"),
            Node(
                package="camera",
                executable="oakd_rgb_publisher",
                name="oakd_rgb_publisher",
                output="screen",
                parameters=[
                    {
                        "width": LaunchConfiguration("width"),
                        "height": LaunchConfiguration("height"),
                        "fps": LaunchConfiguration("fps"),
                        "publish_compressed": LaunchConfiguration("publish_compressed"),
                        "jpeg_quality": LaunchConfiguration("jpeg_quality"),
                    }
                ],
            ),
        ]
    )
