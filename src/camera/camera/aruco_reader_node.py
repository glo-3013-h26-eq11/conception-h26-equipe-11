#!/usr/bin/env python3

import json
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2
import numpy as np


class ArucoReaderNode(Node):
    def __init__(self):
        super().__init__("aruco_reader")

        self.declare_parameter("image_topic", "/oak/rgb/image_raw")
        self.declare_parameter("detections_topic", "aruco_detections")

        image_topic = self.get_parameter("image_topic").value
        detections_topic = self.get_parameter("detections_topic").value

        self.bridge = CvBridge()

        # depthai_ros_driver owns the DAI device exclusively at runtime.
        # Calling dai.Device() here would block forever waiting for a free
        # device.  Use known OAK-D-Lite defaults instead (IMX378 RGB at
        # 1280x720 via 1080P ISP scaled 2/3: fx=fy≈856, cx=640, cy=360).
        instrinsics = [
            [856.0, 0.0, 640.0],
            [0.0, 856.0, 360.0],
            [0.0, 0.0, 1.0],
        ]
        dist = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.get_logger().info("Using default OAK-D-Lite intrinsics (1280x720).")

        self.dist = np.array(dist)
        self.mtx = np.array(instrinsics)

        self.vehicule_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )
        self.intersection_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_5X5_50
        )
        if hasattr(cv2.aruco, "DetectorParameters_create"):
            self.aruco_params = cv2.aruco.DetectorParameters_create()
        else:
            self.aruco_params = cv2.aruco.DetectorParameters()

        self.rgb_sub = self.create_subscription(
            CompressedImage, image_topic, self.rgb_callback, 10
        )

        self.detections_pub = self.create_publisher(String, detections_topic, 10)

        self.get_logger().info("ArUco Reader started")

    def listener_callback(self, rgb_msg: Image):
        self.rgb_callback(rgb_msg)

    def rgb_callback(self, rgb_msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                rgb_msg, desired_encoding="bgr8"
            )

            corners_4x4, ids_4x4, _ = cv2.aruco.detectMarkers(
                frame, self.vehicule_aruco_dict, parameters=self.aruco_params
            )

            corners_5x5, ids_5x5, _ = cv2.aruco.detectMarkers(
                frame, self.intersection_aruco_dict, parameters=self.aruco_params
            )

            detections_4x4 = []
            detections_5x5 = []

            if ids_4x4 is not None:
                for i, marker_id in enumerate(ids_4x4.flatten()):
                    depth = self.calculate_marker_depth(
                        corners_4x4[i], marker_size=0.02
                    )

                    detections_4x4.append({"id": int(marker_id), "depth": float(depth)})

                    self.get_logger().info(f"4x4 Marker {marker_id}: {depth:.3f} m")

            if ids_5x5 is not None:
                for i, marker_id in enumerate(ids_5x5.flatten()):
                    depth = self.calculate_marker_depth(
                        corners_5x5[i], marker_size=0.075
                    )

                    detections_5x5.append({"id": int(marker_id), "depth": float(depth)})

                    self.get_logger().info(f"5x5 Marker {marker_id}: {depth:.3f} m")

            if not detections_4x4 and not detections_5x5:
                return

            payload = {
                "frame_id": rgb_msg.header.frame_id,
                "stamp": {
                    "sec": int(rgb_msg.header.stamp.sec),
                    "nanosec": int(rgb_msg.header.stamp.nanosec),
                },
                "ids_4x4": [d["id"] for d in detections_4x4],
                "ids_5x5": [d["id"] for d in detections_5x5],
                "markers_4x4": detections_4x4,
                "markers_5x5": detections_5x5,
            }

            out = String()
            out.data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            self.detections_pub.publish(out)

        except Exception as e:
            self.get_logger().error(str(e))

    def calculate_marker_depth(self, corner, marker_size):
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            [corner], marker_size, self.mtx, self.dist
        )
        # Euclidean distance (norm of translation vector) — accounts for
        # lateral and vertical offset when approaching at an angle.
        return float(np.linalg.norm(tvecs[0][0]))


def main(args=None):
    rclpy.init(args=args)
    node = ArucoReaderNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
