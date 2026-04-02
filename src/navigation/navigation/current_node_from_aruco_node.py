import json
from typing import Optional

import rclpy
from std_msgs.msg import String, Float32, Bool
from web_interface.system_health_node import HealthPingingNode

SAFE_DISTANCE_TO_CAR = 0.25  # m
CAR_DETECTION_REFRESH = 0.5


class CurrentNodeFromArucoNode(HealthPingingNode):
    def __init__(self):
        super().__init__("current_node_from_aruco", "navigation")

        self._detections_sub = self.create_subscription(
            String,
            "aruco_detections",
            self._detections_callback,
            10,
        )

        self._current_node_pub = self.create_publisher(String, "current_node", 10)

        self._following_car_pub = self.create_publisher(Float32, "distance_to_car", 10)

        self._dangerous_distance_publisher = self.create_publisher(
            Bool, "/car_follower/dangerous_distance", 10
        )

        self.create_timer(CAR_DETECTION_REFRESH, self._publish_distance)

        self.is_car_at_dangerous_distance = False

    def _detections_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
            self._detect_intersections(payload)
            self._detect_cars(payload)

        except Exception:
            pass

    def _detect_intersections(self, payload):
        markers_5x5 = payload.get("markers_5x5", [])
        
        if not markers_5x5:
            return
        
        self.get_logger().info(f"Detected: {len(markers_5x5)} markers")
        
        valid_markers = [m for m in markers_5x5 if m.get("z_forward", 0) >= 0.15]
        
        if not valid_markers:
            self.get_logger().warn("No valid markers according to the z_forward.")
            return
        
        selected_marker = None
        
        front_strict = [m for m in valid_markers if m.get("angle_x_deg", 999) < 10.0]
        if front_strict:
            selected_marker = min(front_strict, key=lambda m: m.get("depth", 9999))
            self.get_logger().info(f"Front strict: Tag {selected_marker['tag']}, angle {selected_marker['angle_x_deg']}°")
        
        if not selected_marker:
            front_wide = [m for m in valid_markers if m.get("angle_x_deg", 999) < 30.0]
            if front_wide:
                selected_marker = min(front_wide, key=lambda m: m.get("depth", 9999))
                self.get_logger().info(f"Front wide: Tag {selected_marker['tag']}, angle {selected_marker['angle_x_deg']}°")
        
        if not selected_marker:
            side = [m for m in valid_markers if m.get("angle_x_deg", 999) < 60.0]
            if side:
                selected_marker = min(side, key=lambda m: m.get("depth", 9999))
                self.get_logger().info(f"Side: Tag {selected_marker['tag']}, angle {selected_marker['angle_x_deg']}°")
        
        if selected_marker:
            marker_id = selected_marker.get("tag")
            distance = selected_marker.get("depth")
            
            out = String()
            out.data = json.dumps({"tag": marker_id, "distance": distance})
            self._current_node_pub.publish(out)
            self.get_logger().info(f"Published: Tag {marker_id}, distance {distance:.2f}m")
        else:
            self.get_logger().warn("No marker selected according to the range < 60 degrees fixed.")
            

    def _detect_cars(self, payload):
        markers_4x4 = payload.get("markers_4x4", [])

        closest_vehicle_dist: Optional[float] = None

        for marker in markers_4x4:

            d = float(marker.get("depth", 9999))
            angle = float(marker.get("angle_x_deg", 0))

            if angle <= 45.0:
                if closest_vehicle_dist is None or d < closest_vehicle_dist:

                    closest_vehicle_dist = d

                    distance = Float32()
                    distance.data = closest_vehicle_dist

                    self._following_car_pub.publish(distance)

                    if d <= SAFE_DISTANCE_TO_CAR:
                        self.is_car_at_dangerous_distance = True

    def _publish_distance(self):
        out = Bool()
        out.data = self.is_car_at_dangerous_distance
        self._dangerous_distance_publisher.publish(out)

        self.is_car_at_dangerous_distance = False


def main(args=None):
    rclpy.init(args=args)
    node = CurrentNodeFromArucoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
