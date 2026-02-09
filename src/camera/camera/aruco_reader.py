#!/usr/bin/env python3

from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Float32MultiArray
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
import cv2
import numpy as np

class ArucoReader(Node):
    def __init__(self):
        super().__init__('aruco_reader')
        
        self.bridge = CvBridge()
        self.latest_depth = None
        
        self.vehicule_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.intersection_aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
        self.aruco_params = cv2.aruco.DetectorParameters_create()
        
        self.depth_sub = self.create_subscription(
            CompressedImage,
            '/oak/stereo/image_raw/compressed',
            self.depth_callback,
            10
        )
        
        self.rgb_sub = self.create_subscription(
            CompressedImage,
            '/oak/rgb/image_raw/compressed',
            self.rgb_callback,
            10
        )
        
        self.detection5x5_pub = self.create_publisher(
            Float32MultiArray,
            '/aruco/detections_5x5',
            10
        )
        
        self.detection4x4_pub = self.create_publisher(
            Float32MultiArray,
            '/aruco/detections_4x4',
            10
        )
        
        self.get_logger().info("ArUco Reader started")
    
    def depth_callback(self, depth_msg):
        """Store aligned depth image"""
        self.latest_depth = self.bridge.compressed_imgmsg_to_cv2(
            depth_msg, 
            desired_encoding='passthrough'
        )
    
    def rgb_callback(self, rgb_msg):
        """Process RGB with aligned depth"""
        if self.latest_depth is None:
            self.get_logger().warn("No depth image yet", throttle_duration_sec=5.0)
            return
        
        try:
            rgb_frame = self.bridge.compressed_imgmsg_to_cv2(rgb_msg, desired_encoding='bgr8')
            
            corners_4x4, ids_4x4, _= cv2.aruco.detectMarkers(
                rgb_frame, 
                self.vehicule_aruco_dict, 
                parameters=self.aruco_params
            )
            
            corners_5x5, ids_5x5, _ = cv2.aruco.detectMarkers(
                rgb_frame, 
                self.intersection_aruco_dict, 
                parameters=self.aruco_params
            )
            
            if ids_4x4 is not None and len(ids_4x4) > 0:
                for i, marker_id in enumerate(ids_4x4):
                    depth = self.get_marker_depth(corners_4x4[i])
                    
                    msg = Float32MultiArray()
                    msg.data = [float(marker_id[0]), depth]
                    self.detection4x4_pub.publish(msg)
                    
                    self.get_logger().info(
                        f"4x4 Marker {marker_id[0]}: {depth:.3f}m"
                    )
            
            if ids_5x5 is not None and len(ids_5x5) > 0:
                for i, marker_id in enumerate(ids_5x5):
                    depth = self.get_marker_depth(corners_5x5[i])
                    
                    msg = Float32MultiArray()
                    msg.data = [float(marker_id[0]), depth]
                    self.detection5x5_pub.publish(msg)
                    
                    self.get_logger().info(
                        f"5x5 Marker {marker_id[0]}: {depth:.3f}m"
                    )
        
        except Exception as e:
            self.get_logger().error(f"Error: {str(e)}")
            import traceback
            self.get_logger().error(traceback.format_exc())
    
    def get_marker_depth(self, corners):
        """Get depth at marker center"""
        corner_points = corners[0]
        center_x = int(np.mean(corner_points[:, 0]))
        center_y = int(np.mean(corner_points[:, 1]))
        
        height, width = self.latest_depth.shape[:2]
        center_x = np.clip(center_x, 0, width - 1)
        center_y = np.clip(center_y, 0, height - 1)
        
        depth_mm = self.latest_depth[center_y, center_x]
        depth_m = float(depth_mm) / 1000.0
        
        if depth_m == 0 or np.isnan(depth_m):
            region_size = 5
            y_start = max(0, center_y - region_size)
            y_end = min(height, center_y + region_size)
            x_start = max(0, center_x - region_size)
            x_end = min(width, center_x + region_size)
            
            region = self.latest_depth[y_start:y_end, x_start:x_end]
            valid_depths = region[(region > 0) & (~np.isnan(region))]
            
            if len(valid_depths) > 0:
                depth_m = float(np.mean(valid_depths)) / 1000.0
            else:
                self.get_logger().warn(
                    f"No valid depth at marker location ({center_x}, {center_y})",
                    throttle_duration_sec=2.0
                )
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

if __name__ == '__main__':
    main()