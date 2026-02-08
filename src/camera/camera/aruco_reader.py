from sensor_msgs.msg import CompressedImage
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import json


class ArucoReader(Node):
    def __init__(self):
        super().__init__("aruco_reader")

        self.bridge = CvBridge()

        self.callback_count = 0

        self.declare_parameter("image_topic", "/oak/rgb/image_rect/compressed")
        self.declare_parameter("detections_topic", "aruco_detections")
        self.declare_parameter("publish_empty", False)
        self.declare_parameter("log_every_n", 10)

        self.image_topic = (
            self.get_parameter("image_topic").get_parameter_value().string_value
        )
        self.detections_topic = (
            self.get_parameter("detections_topic").get_parameter_value().string_value
        )
        self.publish_empty = (
            self.get_parameter("publish_empty").get_parameter_value().bool_value
        )
        self.log_every_n = self.get_parameter("log_every_n").get_parameter_value().integer_value

        self.vehicule_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50
        )
        self.intersection_aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_5X5_50
        )

        self.aruco_params = cv2.aruco.DetectorParameters()

        self.detector_4x4 = cv2.aruco.ArucoDetector(
            self.vehicule_aruco_dict, self.aruco_params
        )
        self.detector_5x5 = cv2.aruco.ArucoDetector(
            self.intersection_aruco_dict, self.aruco_params
        )

        self.detections_publisher = self.create_publisher(String, self.detections_topic, 10)

        self.subscription = self.create_subscription(
            CompressedImage,
            self.image_topic,
            self.listener_callback,
            10,
        )

        self.get_logger().info("Aruco reader started")

    def status_check(self):
        self.get_logger().info(f"Status: Received {self.callback_count} images so far")

    def listener_callback(self, compressed_image):
        self.callback_count += 1

        if self.log_every_n > 0 and self.callback_count % self.log_every_n == 0:
            self.get_logger().info(f"Processing image #{self.callback_count}")

        try:

            cv2_frame = self.bridge.compressed_imgmsg_to_cv2(
                compressed_image, desired_encoding="bgr8"
            )

            corners_4x4, ids_4x4, rejected_4x4 = self.detector_4x4.detectMarkers(
                cv2_frame
            )

            corners_5x5, ids_5x5, rejected_5x5 = self.detector_5x5.detectMarkers(
                cv2_frame
            )

            ids_4x4_list = []
            ids_5x5_list = []
            if ids_4x4 is not None and len(ids_4x4) > 0:
                ids_4x4_list = [int(x) for x in ids_4x4.flatten().tolist()]

            if ids_5x5 is not None and len(ids_5x5) > 0:
                ids_5x5_list = [int(x) for x in ids_5x5.flatten().tolist()]

            if self.publish_empty or ids_4x4_list or ids_5x5_list:
                payload = {
                    "frame_id": compressed_image.header.frame_id,
                    "stamp": {
                        "sec": int(compressed_image.header.stamp.sec),
                        "nanosec": int(compressed_image.header.stamp.nanosec),
                    },
                    "ids_4x4": ids_4x4_list,
                    "ids_5x5": ids_5x5_list,
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

        except Exception as e:
            self.get_logger().error(f"Error processing image: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    aruco_reader = ArucoReader()

    try:
        rclpy.spin(aruco_reader)
    except KeyboardInterrupt:
        pass
    finally:
        aruco_reader.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
