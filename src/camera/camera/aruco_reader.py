#!/usr/bin/env python3

import json
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Float32MultiArray, String
from cv_bridge import CvBridge

import cv2
import numpy as np
import depthai as dai


class ArucoReader(Node):
    def __init__(self):
        super().__init__('aruco_reader')

        self.bridge = CvBridge()

        with dai.Device() as device:
            calib = device.readCalibration()

            instrinsics = calib.getCameraIntrinsics(
                dai.CameraBoardSocket.RGB,
                1280,
                720,
            )

            dist = calib.getDistortionCoefficients(dai.CameraBoardSocket.RGB)

        self.dist = np.array(dist)
        self.mtx = np.array(instrinsics)

        self.vehicule_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )
        self.intersection_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_5X5_50
        )
        self.aruco_params = cv2.aruco.DetectorParameters_create()

        self.rgb_sub = self.create_subscription(
            CompressedImage,
            '/oak/rgb/image_raw/compressed',
            self.rgb_callback,
            10,
        )

        self.detection4x4_pub = self.create_publisher(
            Float32MultiArray,
            '/aruco/detections_4x4',
            10,
        )

        self.detection5x5_pub = self.create_publisher(
            Float32MultiArray,
            '/aruco/detections_5x5',
            10,
        )

        # JSON compact pour navigation (un message par frame)
        self.detections_pub = self.create_publisher(String, 'aruco_detections', 10)

        self.get_logger().info("ArUco Reader started")

    # Alias pour compatibilité avec certains launch/tests
    def listener_callback(self, rgb_msg: CompressedImage):
        self.rgb_callback(rgb_msg)

    def rgb_callback(self, rgb_msg: CompressedImage):
        try:
            frame = self.bridge.compressed_imgmsg_to_cv2(
                rgb_msg, desired_encoding='bgr8'
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
                    z_m = self.calculate_marker_depth(corners_4x4[i], marker_size=0.02)

                    msg = Float32MultiArray()
                    msg.data = [float(marker_id), z_m]
                    self.detection4x4_pub.publish(msg)

                    detections_4x4.append({"id": int(marker_id), "z_m": float(z_m)})

                    self.get_logger().info(f"4x4 Marker {marker_id}: {z_m:.3f} m")

            if ids_5x5 is not None:
                for i, marker_id in enumerate(ids_5x5.flatten()):
                    z_m = self.calculate_marker_depth(corners_5x5[i], marker_size=0.075)

                    msg = Float32MultiArray()
                    msg.data = [float(marker_id), z_m]
                    self.detection5x5_pub.publish(msg)

                    detections_5x5.append({"id": int(marker_id), "z_m": float(z_m)})

                    self.get_logger().info(f"5x5 Marker {marker_id}: {z_m:.3f} m")

            if not detections_4x4 and not detections_5x5:
                return

            payload = {
                "v": 1,
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
        return float(tvecs[0][0][2])


def main(args=None):
    rclpy.init(args=args)
    node = ArucoReader()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
