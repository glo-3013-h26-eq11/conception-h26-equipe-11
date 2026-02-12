import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    depthai_share_dir = get_package_share_directory("depthai_ros_driver")
    depthai_rgbd_pcl_launch_path = os.path.join(
        depthai_share_dir,
        "launch",
        "rgbd_pcl.launch.py",
    )
    depthai_camera_launch_path = os.path.join(
        depthai_share_dir,
        "launch",
        "camera.launch.py",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "start_depthai",
                default_value="true",
                description="Start depthai_ros_driver inside this launch.",
            ),
            DeclareLaunchArgument(
                "use_rgbd_pcl",
                default_value="true",
                description=(
                    "If true, start depthai_ros_driver/rgbd_pcl.launch.py (recommended). "
                    "If false, start depthai_ros_driver/camera.launch.py."
                ),
            ),
            DeclareLaunchArgument(
                "image_topic",
                default_value="/oak/rgb/image_rect/compressed",
            ),
            DeclareLaunchArgument(
                "detections_topic",
                default_value="aruco_detections",
            ),
            DeclareLaunchArgument("publish_empty", default_value="false"),
            DeclareLaunchArgument("log_every_n", default_value="10"),
            GroupAction(
                actions=[
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(depthai_rgbd_pcl_launch_path),
                        condition=IfCondition(LaunchConfiguration("use_rgbd_pcl")),
                    ),
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(depthai_camera_launch_path),
                        condition=UnlessCondition(
                            LaunchConfiguration("use_rgbd_pcl")
                        ),
                    ),
                ],
                condition=IfCondition(LaunchConfiguration("start_depthai")),
            ),
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
