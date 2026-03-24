import json
from typing import Optional

import rclpy
from std_msgs.msg import String, Float32
from web_interface.system_health_node import HealthPingingNode


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

            d = float(marker.get("depth", 9999))
            angle = float(marker.get("angle_x_deg", 0))
            z_fwd = float(marker.get("z_forward", 0))
            marker_id = marker.get("tag")

            if d <= 1.0 and angle <= 15.0 and z_fwd >= 0.15:

                if closest_stop_dist is None or d < closest_stop_dist:

                    closest_stop_dist = d

                    out = String()
                    out.data = json.dumps(
                        {"tag": marker_id, "distance": closest_stop_dist}
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
