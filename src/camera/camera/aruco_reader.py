from sensor_msgs.msg import CompressedImage
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
import cv2
import numpy as np

class ArucoReader(Node):
    def __init__(self):
        super().__init__('aruco_reader')
        
        self.bridge = CvBridge()
        
        self.vehicule_aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.intersection_aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
        
        self.aruco_params = cv2.aruco.DetectorParameters()
        
        self.detector_4x4 = cv2.aruco.ArucoDetector(self.vehicule_aruco_dict, self.aruco_params)
        self.detector_5x5 = cv2.aruco.ArucoDetector(self.intersection_aruco_dict, self.aruco_params)
        
        self.subscription = self.create_subscription(
            CompressedImage,
            '/oak/rgb/image_rect/',
            self.listener_callback,
            10
        )
        
        self.get_logger().info("Aruco reader started")
        
    def status_check(self):
        self.get_logger().info(f"Status: Received {self.callback_count} images so far")
    
    def listener_callback(self, compressed_image):
        self.callback_count += 1
        
        if self.callback_count % 10 == 0:
            self.get_logger().info(f"Processing image #{self.callback_count}")
            
        try:
            
            cv2_frame = self.bridge.compressed_imgmsg_to_cv2(
                compressed_image, 
                desired_encoding='bgr8' 
            )
            
            corners_4x4, ids_4x4, rejected_4x4 = self.detector_4x4.detectMarkers(cv2_frame)
            
            corners_5x5, ids_5x5, rejected_5x5 = self.detector_5x5.detectMarkers(cv2_frame)
            
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

if __name__ == '__main__':
    main()

