import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from navigation.map import Map


class ArucoLocalizerNode(Node):
    def __init__(self):
        super().__init__("aruco_localizer_node")

        self.create_subscription(
            String,
            "map_manager/parsed_map_topic",
            self.map_callback,
            10,
        )
        self.create_subscription(
            String,
            "aruco_detections",
            self.aruco_callback,
            10,
        )
        self.current_node_pub = self.create_publisher(String, "current_node", 10)

        self.tag_to_node: dict[int, str] = {}
        self.last_published_node: str | None = None

    def map_callback(self, msg: String) -> None:
        parsed_map = Map.from_json(msg.data)
        self.tag_to_node = {
            map_node.tag: map_node.id for map_node in parsed_map.map_nodes.values()
        }

    def aruco_callback(self, msg: String) -> None:
        if not self.tag_to_node:
            return

        payload = json.loads(msg.data)
        markers = payload.get("markers_4x4", [])
        if not markers:
            return

        nearest_marker = min(
            markers, key=lambda marker: marker.get("depth", float("inf"))
        )
        marker_id = int(nearest_marker["id"])
        node_id = self.tag_to_node.get(marker_id)
        if node_id is None or node_id == self.last_published_node:
            return

        out_msg = String()
        out_msg.data = node_id
        self.current_node_pub.publish(out_msg)
        self.last_published_node = node_id


def main(args=None):
    rclpy.init(args=args)
    node = ArucoLocalizerNode()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
