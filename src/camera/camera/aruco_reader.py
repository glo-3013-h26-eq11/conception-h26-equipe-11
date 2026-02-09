from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import Float32MultiArray, String
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import numpy as np
import message_filters
import json

class ArucoReader(Node):
    def __init__(self):
        super().__init__("aruco_reader")

        self.bridge = CvBridge()
        self.latest_depth = None
        
        self.vehicule_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.intersection_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
        self.aruco_params = cv2.aruco.DetectorParameters_create()
        
        self.depth_sub = self.create_subscription(
            Image,
            '/oak/stereo/image_raw',
            self.depth_callback,
            10
        )
        
        self.rgb_sub = self.create_subscription(
            Image,
            '/oak/rgb/image_raw',
            self.rgbd_callback,
            10
        )
        
        self.aruco_5x5_publisher = self.create_publisher(
            Float32MultiArray,
            '/aruco/_depth_5x5_ids',
            10
        )
        
        self.aruco_4x4_publisher = self.create_publisher(
            Float32MultiArray,
            '/aruco/depth_4x4_ids',
            10
        )
        
        
        self.get_logger().info("Aruco reader started")
    
    def depth_callback(self, depth_msg):
        self.latest_depth = self.bridge.imgmsg_to_cv2(
            depth_msg, 
            desired_encoding='passthrough'
        )
        
    def status_check(self):
        self.get_logger().info(f"Status: Received {self.callback_count} images so far")
    
    def rgbd_callback(self, rgb_msg, depth_msg):
        if self.latest_depth is None:
            return
        
        try:
            
            rgb_frame = self.bridge.imgmsg_to_cv2(
                rgb_msg, 
                desired_encoding='bgr8' 
            )
            
            corners_4x4, ids_4x4, rejected_4x4 = self.detector_4x4.detectMarkers(rgb_frame)
            
            corners_5x5, ids_5x5, rejected_5x5 = self.detector_5x5.detectMarkers(rgb_frame)
            
            if ids_4x4 is not None:
                for i, marker_id in enumerate(ids_4x4):
                    depth = self.get_marker_depth(corners_4x4[i])
                    
                    msg = Float32MultiArray()
                    msg.data = [float(marker_id[0]), depth]
                    self.detection_pub.publish(msg)
                    
                    self.get_logger().info(
                        f"4x4 Marker {marker_id[0]}: {depth:.3f}m"
                    )
            
            if ids_5x5 is not None:
                for i, marker_id in enumerate(ids_5x5):
                    depth = self.get_marker_depth(corners_5x5[i])
                    
                    msg = Float32MultiArray()
                    msg.data = [float(marker_id[0]), depth]
                    self.detection_pub.publish(msg)
                    
                    self.get_logger().info(
                        f"5x5 Marker {marker_id[0]}: {depth:.3f}m"
                    )
        
        except Exception as e:
            self.get_logger().error(f"Error: {str(e)}")
    
    def get_marker_depth(self, corners):
        
        corner_points = corners[0]
        center_x = int(np.mean(corner_points[:, 0]))
        center_y = int(np.mean(corner_points[:, 1]))
        
        height, width = self.latest_depth.shape[:2]
        center_x = np.clip(center_x, 0, width - 1)
        center_y = np.clip(center_y, 0, height - 1)
        
        depth_mm = self.latest_depth[center_y, center_x]
        depth_m = depth_mm / 1000.0
        
        if depth_m == 0 or np.isnan(depth_m):
            region_size = 5
            y_start = max(0, center_y - region_size)
            y_end = min(height, center_y + region_size)
            x_start = max(0, center_x - region_size)
            x_end = min(width, center_x + region_size)
            
            region = self.latest_depth[y_start:y_end, x_start:x_end]
            valid_depths = region[(region > 0) & (~np.isnan(region))]
            
            if len(valid_depths) > 0:
                depth_m = np.mean(valid_depths) / 1000.0
            else:
                self.get_logger().warn("No valid depth at marker location!")
                depth_m = 0.0
        
        return depth_m
    
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
