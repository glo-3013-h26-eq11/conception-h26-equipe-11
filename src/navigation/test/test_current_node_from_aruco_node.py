import json
import time
import pytest
import rclpy
from std_msgs.msg import String, Float32, Bool

from navigation.current_node_from_aruco_node import (
    CurrentNodeFromArucoNode,
    SAFE_DISTANCE_TO_CAR,
)


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


class StringSubscriber:
    def __init__(self, node, topic_name):
        self.sub = node.create_subscription(String, topic_name, self.cb, 10)
        self.received = []

    def cb(self, msg: String):
        self.received.append(json.loads(msg.data))


class FloatSubscriber:
    def __init__(self, node, topic_name):
        self.sub = node.create_subscription(Float32, topic_name, self.cb, 10)
        self.received = []

    def cb(self, msg: Float32):
        self.received.append(msg.data)


class BoolSubscriber:
    def __init__(self, node, topic_name):
        self.sub = node.create_subscription(Bool, topic_name, self.cb, 10)
        self.received = []

    def cb(self, msg: Bool):
        self.received.append(msg.data)


class StringPublisher:
    def __init__(self, node, topic_name):
        self.pub = node.create_publisher(String, topic_name, 10)

    def publish(self, payload):
        data = String()
        data.data = json.dumps(payload)
        self.pub.publish(data)


def test_when_detect_aruco_5x5_less_1m_less_15deg_zfwd_g_15_then_publish(node):
    payload = {"markers_5x5": [{"depth": 0.8, "angle_x_deg": 7.0, "z_forward": 0.2}]}

    subscriber = StringSubscriber(node, "current_node")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    assert len(subscriber.received) == 1


def test_when_detect_aruco_5x5_bigger_1m_less_15deg_zfwd_g_15_then_not_publish(node):
    payload = {"markers_5x5": [{"depth": 1.1, "angle_x_deg": 7.0, "z_forward": 0.2}]}

    subscriber = StringSubscriber(node, "current_node")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    assert len(subscriber.received) == 0


def test_when_detect_aruco_5x5_less_1m_bigger_15deg_zfwd_g_15_then_publish(node):
    payload = {"markers_5x5": [{"depth": 0.8, "angle_x_deg": 16.0, "z_forward": 0.2}]}

    subscriber = StringSubscriber(node, "current_node")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    assert len(subscriber.received) == 0


def test_when_detect_aruco_5x5_publish_distance_and_tag(node):
    payload = {
        "markers_5x5": [{"depth": 0.8, "angle_x_deg": 7.0, "z_forward": 0.2, "tag": 1}]
    }

    subscriber = StringSubscriber(node, "current_node")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    assert subscriber.received[0]["distance"] == 0.8
    assert subscriber.received[0]["tag"] == 1


def test_when_detect_aruco_4x4_less_45_deg_publish(node):
    payload = {"markers_4x4": [{"depth": 0.8, "angle_x_deg": 7.0}]}

    subscriber = FloatSubscriber(node, "distance_to_car")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    assert len(subscriber.received) == 1


def test_when_detect_aruco_4x4_bigger_45_deg_no_publish(node):
    payload = {"markers_4x4": [{"depth": 0.8, "angle_x_deg": 46.0}]}

    subscriber = FloatSubscriber(node, "distance_to_car")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    assert len(subscriber.received) == 0


def test_when_detect_aruco_4x4_lesser_45_deg_less_safe_distance_publish_dangerous_distance(
    node,
):
    payload = {
        "markers_4x4": [{"depth": SAFE_DISTANCE_TO_CAR - 0.1, "angle_x_deg": 7.0}]
    }

    subscriber = BoolSubscriber(node, "/car_follower/dangerous_distance")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.1)

    assert len(subscriber.received) == 1
    assert subscriber.received[0]


def test_when_detect_aruco_4x4_less_safe_distance_publish_dangerous_distance_than_safe_distance(
    node,
):
    payload = {
        "markers_4x4": [{"depth": SAFE_DISTANCE_TO_CAR - 0.1, "angle_x_deg": 7.0}]
    }

    subscriber = BoolSubscriber(node, "/car_follower/dangerous_distance")

    publisher = StringPublisher(node, "aruco_detections")

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    publisher.publish(payload)

    start = time.time()
    while time.time() - start < 5.0:
        rclpy.spin_once(node, timeout_sec=0.1)

    assert len(subscriber.received) > 1
    assert not subscriber.received[-1]
