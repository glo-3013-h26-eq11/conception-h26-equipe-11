#!/usr/bin/env python3

import json
from typing import Dict

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CurrentNodeFromArucoNode(Node):
    def __init__(self):
        super().__init__("current_node_from_aruco")

        self._tag_to_node: Dict[int, str] = {}

        self._map_sub = self.create_subscription(
            String,
            "map_manager/parsed_map_topic",
            self._map_callback,
            10,
        )
        self._detections_sub = self.create_subscription(
            String,
            "aruco_detections",
            self._detections_callback,
            10,
        )
        self._current_node_pub = self.create_publisher(String, "current_node", 10)

    def _map_callback(self, msg: String) -> None:
        map_dict = json.loads(msg.data)
        self._tag_to_node = self._build_tag_to_node(map_dict)

    def _build_tag_to_node(self, map_dict: dict) -> Dict[int, str]:
        tag_to_node: Dict[int, str] = {}
        for node_id, node_data in map_dict.items():
            tag = node_data["tag"]
            tag_to_node[int(tag)] = str(node_id)
        return tag_to_node

    def _detections_callback(self, msg: String) -> None:
        payload = json.loads(msg.data)
        candidate_ids = payload.get("ids_5x5", [])

        for marker_id in candidate_ids:
            node_id = self._tag_to_node.get(int(marker_id))
            if node_id is not None:
                out = String()
                out.data = node_id
                self._current_node_pub.publish(out)
                return


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
