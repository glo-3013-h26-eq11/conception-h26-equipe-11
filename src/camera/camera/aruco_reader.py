from sensor_msgs.msg import CompressedImage
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
import cv2


class ArucoReader(Node):
    def __init__(self):
        super().__init__('aruco_reader')
        self.subscription = self.create_subscription(
            CompressedImage,
            '/oak/rgb/image_rect/compressed',
            self.listener_callback,
            10)
    
        self.get_logger().info("Aruco reader started")
    
    def listener_callback(self, compressedImage):
        cv2_frame = CvBridge().compressed_imgmsg_to_cv2(compressedImage, desired_encoding='passthrough')
        vehicule_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4x4_50)
        intersection_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5x5_50)
        aruco_params = cv2.aruco.DetectorParameters_create()
        
        (corners_4x4, ids_4x4, rejected_4x4) = cv2.aruco.detectMarkers(cv2_frame, vehicule_aruco_dict, parameters=aruco_params)
        
        (corners_5x5, ids_5x5, rejected_5x5) = cv2.aruco.detectMarkers(cv2_frame, intersection_aruco_dict, parameters=aruco_params)
        
        if ids_4x4 is not None:
            self.get_logger().info(f"Detected 4x4 Aruco IDs: {ids_4x4.flatten()}")
        else:
            self.get_logger().info("No 4x4 Aruco markers detected.")
            
        if ids_5x5 is not None:
            self.get_logger().info(f"Detected 5x5 Aruco IDs: {ids_5x5.flatten()}")
        else:
            self.get_logger().info("No 5x5 Aruco markers detected.")
            
        


def main(args=None):
    rclpy.init(args=args)

    aruco_reader = ArucoReader()

    rclpy.spin(aruco_reader)
    
    aruco_reader.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

