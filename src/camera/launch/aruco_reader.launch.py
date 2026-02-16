from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "image_topic", default_value="/oak/rgb/image_rect/compressed"
            ),
            DeclareLaunchArgument("detections_topic", default_value="aruco_detections"),
            DeclareLaunchArgument("publish_empty", default_value="false"),
            DeclareLaunchArgument("log_every_n", default_value="10"),
            Node(
                package="camera",
                executable="aruco_reader",
                name="aruco_reader",
                output="screen",
                parameters=[
                    {
                        "image_topic": LaunchConfiguration("image_topic"),
                        "detections_topic": LaunchConfiguration("detections_topic"),
                        "publish_empty": LaunchConfiguration("publish_empty"),
                        "log_every_n": LaunchConfiguration("log_every_n"),
                    }
                ],
            ),
        ]
    )
