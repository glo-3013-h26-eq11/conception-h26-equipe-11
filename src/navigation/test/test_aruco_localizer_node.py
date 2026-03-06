import json

import pytest
import rclpy
from std_msgs.msg import String

from navigation.aruco_localizer_node import ArucoLocalizerNode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    localizer = ArucoLocalizerNode()
    yield localizer
    localizer.destroy_node()


def test_given_map_and_aruco_detection_when_tag_known_then_publish_current_node(node):
    received = []

    def call_back(msg):
        received.append(msg.data)

    node.create_subscription(String, "current_node", call_back, 10)

    map_msg = String()
    map_msg.data = json.dumps(
        {
            "A1": {
                "id": "A1",
                "tag": 1,
                "left": None,
                "right": None,
                "straight": None,
            }
        }
    )
    node.map_callback(map_msg)

    aruco_msg = String()
    aruco_msg.data = json.dumps(
        {
            "markers_4x4": [{"id": 1, "depth": 0.5}],
            "markers_5x5": [],
        }
    )

    node.aruco_callback(aruco_msg)
    rclpy.spin_once(node, timeout_sec=0.1)

    assert received == ["A1"]


def test_given_unknown_tag_when_aruco_detected_then_publish_nothing(node):
    received = []

    def call_back(msg):
        received.append(msg.data)

    node.create_subscription(String, "current_node", call_back, 10)

    map_msg = String()
    map_msg.data = json.dumps(
        {
            "A1": {
                "id": "A1",
                "tag": 1,
                "left": None,
                "right": None,
                "straight": None,
            }
        }
    )
    node.map_callback(map_msg)

    aruco_msg = String()
    aruco_msg.data = json.dumps(
        {
            "markers_4x4": [{"id": 99, "depth": 0.5}],
            "markers_5x5": [],
        }
    )

    node.aruco_callback(aruco_msg)
    rclpy.spin_once(node, timeout_sec=0.1)

    assert received == []
