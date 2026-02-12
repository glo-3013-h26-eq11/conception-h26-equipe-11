import json
from typing import Any

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, CompressedImage
from std_msgs.msg import String

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None


def _create_aruco_parameters():
    if hasattr(cv2.aruco, "DetectorParameters"):
        return cv2.aruco.DetectorParameters()

    if hasattr(cv2.aruco, "DetectorParameters_create"):
        return cv2.aruco.DetectorParameters_create()

    raise AttributeError(
        "cv2.aruco has no DetectorParameters or DetectorParameters_create"
    )


class _LegacyArucoDetector:

    def __init__(self, dictionary, parameters):
        self._dictionary = dictionary
        self._parameters = parameters

    def detectMarkers(self, frame):
        return cv2.aruco.detectMarkers(
            frame, self._dictionary, parameters=self._parameters
        )


def _create_aruco_detector(dictionary, parameters):
    if hasattr(cv2.aruco, "ArucoDetector"):
        return cv2.aruco.ArucoDetector(dictionary, parameters)

    if hasattr(cv2.aruco, "detectMarkers"):
        return _LegacyArucoDetector(dictionary, parameters)

    raise AttributeError("cv2.aruco has no ArucoDetector or detectMarkers")


def _ids_to_list(ids: Any) -> list[int]:
    if ids is None:
        return []
    if len(ids) == 0:
        return []
    return [int(x) for x in ids.flatten().tolist()]


def _build_stamp(header: Any) -> dict[str, int]:
    return {
        "sec": int(header.stamp.sec),
        "nanosec": int(header.stamp.nanosec),
    }


class ArucoReader(Node):
    def __init__(self):
        super().__init__("aruco_reader")

        self.bridge = CvBridge()
        self.callback_count = 0

        self.declare_parameter("image_topic", "/oak/rgb/image_rect/compressed")
        self.declare_parameter("camera_info_topic", "/oak/rgb/camera_info")
        self.declare_parameter("detections_topic", "aruco_detections")
        self.declare_parameter("publish_empty", False)
        self.declare_parameter("log_every_n", 10)
        self.declare_parameter("marker_size_4x4_m", 0.02)
        self.declare_parameter("marker_size_5x5_m", 0.075)

        self.image_topic = (
            self.get_parameter("image_topic").get_parameter_value().string_value
        )
        self.camera_info_topic = (
            self.get_parameter("camera_info_topic").get_parameter_value().string_value
        )
        self.detections_topic = (
            self.get_parameter("detections_topic").get_parameter_value().string_value
        )
        self.publish_empty = (
            self.get_parameter("publish_empty").get_parameter_value().bool_value
        )
        self.log_every_n = (
            self.get_parameter("log_every_n").get_parameter_value().integer_value
        )
        self.marker_size_4x4_m = (
            self.get_parameter("marker_size_4x4_m").get_parameter_value().double_value
        )
        self.marker_size_5x5_m = (
            self.get_parameter("marker_size_5x5_m").get_parameter_value().double_value
        )

        self._camera_matrix = None
        self._dist_coeffs = None
        self._camera_info_received = False

        self.vehicule_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )
        self.intersection_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_5X5_50
        )

        self.aruco_params = _create_aruco_parameters()
        self.detector_4x4 = _create_aruco_detector(
            self.vehicule_aruco_dict, self.aruco_params
        )
        self.detector_5x5 = _create_aruco_detector(
            self.intersection_aruco_dict, self.aruco_params
        )

        self.detections_publisher = self.create_publisher(
            String, self.detections_topic, 10
        )

        self.create_subscription(
            CameraInfo,
            self.camera_info_topic,
            self._camera_info_callback,
            qos_profile_sensor_data,
        )

        self.create_subscription(
            CompressedImage,
            self.image_topic,
            self.listener_callback,
            qos_profile_sensor_data,
        )

        self.get_logger().info("Aruco reader is ready")
        self.get_logger().info(
            f"Waiting for CameraInfo on '{self.camera_info_topic}' to enable z_m"
        )

    def _camera_info_callback(self, msg: CameraInfo) -> None:
        if np is None:
            return

        try:
            self._camera_matrix = np.array(msg.k, dtype=float).reshape(3, 3)
            self._dist_coeffs = np.array(msg.d, dtype=float)

            if not self._camera_info_received:
                self._camera_info_received = True
                self.get_logger().info(
                    f"CameraInfo received from '{self.camera_info_topic}'; z_m enabled"
                )
        except Exception:
            self._camera_matrix = None
            self._dist_coeffs = None

    def _estimate_z_m(self, corner: Any, marker_size_m: float):
        if np is None:
            return None
        if self._camera_matrix is None or self._dist_coeffs is None:
            return None
        if not hasattr(cv2.aruco, "estimatePoseSingleMarkers"):
            return None

        try:
            _rvecs, tvecs, _obj_points = cv2.aruco.estimatePoseSingleMarkers(
                [corner], marker_size_m, self._camera_matrix, self._dist_coeffs
            )
            return float(tvecs[0][0][2])
        except Exception:
            return None

    def _build_detections(
        self,
        ids_list: list[int],
        corners: Any,
        marker_size_m: float,
    ) -> list[dict[str, Any]]:
        if not ids_list or not corners:
            return []

        detections: list[dict[str, Any]] = []
        for idx, marker_id in enumerate(ids_list):
            if idx >= len(corners):
                break
            z_m = self._estimate_z_m(corners[idx], marker_size_m)
            detections.append({"id": marker_id, "z_m": z_m})
        return detections

    def listener_callback(self, compressed_image: CompressedImage) -> None:
        self.callback_count += 1

        if self.log_every_n > 0 and self.callback_count % self.log_every_n == 0:
            self.get_logger().info(f"Processing image #{self.callback_count}")

        try:
            cv2_frame = self.bridge.compressed_imgmsg_to_cv2(
                compressed_image, desired_encoding="bgr8"
            )

            corners_4x4, ids_4x4, _rejected_4x4 = self.detector_4x4.detectMarkers(
                cv2_frame
            )
            corners_5x5, ids_5x5, _rejected_5x5 = self.detector_5x5.detectMarkers(
                cv2_frame
            )

            ids_4x4_list = _ids_to_list(ids_4x4)
            ids_5x5_list = _ids_to_list(ids_5x5)

            detections_4x4 = self._build_detections(
                ids_4x4_list, corners_4x4, self.marker_size_4x4_m
            )
            detections_5x5 = self._build_detections(
                ids_5x5_list, corners_5x5, self.marker_size_5x5_m
            )

            if self.publish_empty or ids_4x4_list or ids_5x5_list:
                payload = {
                    "frame_id": compressed_image.header.frame_id,
                    "stamp": _build_stamp(compressed_image.header),
                    "ids_4x4": ids_4x4_list,
                    "ids_5x5": ids_5x5_list,
                    "detections_4x4": detections_4x4,
                    "detections_5x5": detections_5x5,
                    "has_camera_info": self._camera_matrix is not None,
                    "camera_info_topic": self.camera_info_topic,
                    "image_topic": self.image_topic,
                    "callback_count": int(self.callback_count),
                }

                out_msg = String()
                out_msg.data = json.dumps(payload)
                self.detections_publisher.publish(out_msg)

            if ids_4x4 is not None and len(ids_4x4) > 0:
                self.get_logger().info(f"Detected 4x4 Aruco IDs: {ids_4x4.flatten()}")
            if ids_5x5 is not None and len(ids_5x5) > 0:
                self.get_logger().info(f"Detected 5x5 Aruco IDs: {ids_5x5.flatten()}")

        except Exception as exc:
            self.get_logger().error(f"Error processing image: {str(exc)}")


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


if __name__ == "__main__":
    main()
