import json

import pytest
import rclpy
from std_msgs.msg import String

from navigation.current_node_from_aruco_node import CurrentNodeFromArucoNode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    n = CurrentNodeFromArucoNode()
    yield n
    n.destroy_node()


def _capture_topic(node, topic_name, timeout_sec=0.2):
    received = []

    def on_msg(msg):
        received.append(msg.data)

    node.create_subscription(String, topic_name, on_msg, 10)
    return received


def test_given_map_and_detection_when_marker_in_map_then_publishes_current_node(node):
    received = _capture_topic(node, "current_node")

    map_payload = {
        "A1": {"id": "A1", "tag": 1, "left": "ZC1", "straight": None, "right": None},
        "A2": {"id": "A2", "tag": 2, "left": None, "straight": "A1", "right": None},
    }
    detections_payload = {"ids_5x5": [2]}

    node._map_callback(String(data=json.dumps(map_payload)))
    node._detections_callback(String(data=json.dumps(detections_payload)))
    rclpy.spin_once(node, timeout_sec=0.2)

    assert received == ["A2"]
