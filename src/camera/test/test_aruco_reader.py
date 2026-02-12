
import json

import pytest
import rclpy
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


class FakeIds:
    def __init__(self, values):
        self._values = list(values)

    def __len__(self):
        return len(self._values)

    def flatten(self):
        return self

    def tolist(self):
        return list(self._values)


class FakeDetector:
    def __init__(self, ids):
        self._ids = ids

    def detectMarkers(self, _frame):
        return ([], self._ids, [])


class FakeAruco:
    DICT_4X4_50 = object()
    DICT_5X5_50 = object()

    @staticmethod
    def getPredefinedDictionary(_which):
        return object()

    @staticmethod
    def DetectorParameters():
        return object()

    @staticmethod
    def ArucoDetector(_dictionary, _params):
        raise AssertionError("ArucoDetector should be monkeypatched per test")


class FakeBridge:
    def compressed_imgmsg_to_cv2(self, _msg, desired_encoding="bgr8"):
        return object()


def _make_compressed_image(frame_id="oak", sec=1, nanosec=2):
    msg = CompressedImage()
    msg.header.frame_id = frame_id
    msg.header.stamp.sec = sec
    msg.header.stamp.nanosec = nanosec
    return msg


def test_publishes_ids_when_detected(monkeypatch):
    import camera.aruco_reader as ar

    monkeypatch.setattr(ar, "CvBridge", FakeBridge)

    if not hasattr(ar.cv2, "aruco"):
        monkeypatch.setattr(ar.cv2, "aruco", FakeAruco, raising=False)

    ar.cv2.aruco = FakeAruco

    def fake_aruco_detector(_dictionary, _params):
        return FakeDetector(FakeIds([1, 2]))

    monkeypatch.setattr(ar.cv2.aruco, "ArucoDetector", fake_aruco_detector)

    node = ar.ArucoReader()

    received = []

    listener = rclpy.create_node("aruco_detections_listener")

    def cb(msg: String):
        received.append(msg.data)

    listener.create_subscription(String, "aruco_detections", cb, 10)

    node.listener_callback(_make_compressed_image(sec=123, nanosec=456))
    rclpy.spin_once(listener, timeout_sec=0.2)

    assert len(received) == 1
    payload = json.loads(received[0])
    assert payload["ids_4x4"] == [1, 2]
    assert payload["ids_5x5"] == [1, 2]
    assert payload["stamp"]["sec"] == 123
    assert payload["stamp"]["nanosec"] == 456

    node.destroy_node()
    listener.destroy_node()


def test_does_not_publish_when_no_detections(monkeypatch):
    import camera.aruco_reader as ar

    monkeypatch.setattr(ar, "CvBridge", FakeBridge)

    if not hasattr(ar.cv2, "aruco"):
        monkeypatch.setattr(ar.cv2, "aruco", FakeAruco, raising=False)

    ar.cv2.aruco = FakeAruco

    def fake_aruco_detector(_dictionary, _params):
        return FakeDetector(None)

    monkeypatch.setattr(ar.cv2.aruco, "ArucoDetector", fake_aruco_detector)

    node = ar.ArucoReader()

    received = []

    listener = rclpy.create_node("aruco_detections_listener_empty")

    def cb(msg: String):
        received.append(msg.data)

    listener.create_subscription(String, "aruco_detections", cb, 10)

    node.listener_callback(_make_compressed_image())
    rclpy.spin_once(listener, timeout_sec=0.2)

    assert received == []

    node.destroy_node()
    listener.destroy_node()
