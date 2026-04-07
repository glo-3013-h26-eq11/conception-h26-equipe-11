import json
from typing import Optional

import rclpy
from std_msgs.msg import String, Float32, Bool
from web_interface.system_health_node import HealthPingingNode
from numpy import abs

SAFE_DISTANCE_TO_CAR = 0.25  # m
CAR_DETECTION_REFRESH = 0.5

FRONT_CONE_DETECTION = 75.0


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

        closest_stop_dist: Optional[float] = None

        for marker in markers_5x5:

            depth = float(marker.get("depth", 9999))
            angle = float(marker.get("angle_x_deg", 0))
            z_forward = float(marker.get("z_forward", 0))
            tag_angle = float(marker.get("tag_angle", 0))
            marker_id = marker.get("tag")

            if depth <= 1.0 and angle <= FRONT_CONE_DETECTION and z_forward >= 0.15:

                if abs(tag_angle) < 45.0:
                    if closest_stop_dist is None or depth < closest_stop_dist:

                        closest_stop_dist = depth

                        out = String()
                        out.data = json.dumps(
                            {
                                "tag": marker_id,
                                "distance": closest_stop_dist,
                                "angle": tag_angle,
                            }
                        )
                        self._current_node_pub.publish(out)

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
