import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    depthai_camera_launch_path = os.path.join(
        get_package_share_directory("depthai_ros_driver"),
        "launch",
        "camera.launch.py",
    )

    # RGB-only params file: avoids RGBD pipeline that crashes OV7251 mono sensors
    # on OAK-D-Lite (those sensors only support 480P/400P, not the 720P RGBD needs).
    oakd_lite_params = os.path.join(
        get_package_share_directory("camera"),
        "config",
        "oakd_lite_rgb.yaml",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_depthai",
                default_value="true",
                description="Start depthai_ros_driver inside this launch.",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=oakd_lite_params,
                description="Path to depthai_ros_driver params YAML file.",
            ),
            DeclareLaunchArgument(
                "image_topic",
                default_value="/oak/rgb/image_raw",
            ),
            DeclareLaunchArgument(
                "detections_topic",
                default_value="aruco_detections",
            ),
            DeclareLaunchArgument("publish_empty", default_value="false"),
            DeclareLaunchArgument("log_every_n", default_value="10"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(depthai_camera_launch_path),
                launch_arguments={
                    "params_file": LaunchConfiguration("params_file"),
                }.items(),
                condition=IfCondition(LaunchConfiguration("start_depthai")),
            ),
            Node(
                package="camera",
                executable="aruco_reader_node",
                name="aruco_reader_node",
                output="screen",
                respawn_delay=2.0,
                respawn=True,
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
