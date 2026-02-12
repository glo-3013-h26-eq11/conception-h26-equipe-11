import json

import pytest
import rclpy
from sensor_msgs.msg import CameraInfo
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
    def __init__(self, ids, corners=None):
        self._ids = ids
        self._corners = corners

    def detectMarkers(self, _frame):
        corners = self._corners
        if corners is None:
            if self._ids is None:
                corners = []
            else:
                corners = [object() for _ in range(len(self._ids))]

        return (corners, self._ids, [])


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
    assert payload["image_topic"]
    assert payload["callback_count"] >= 1
    assert payload["has_camera_info"] in (True, False)
    assert "detections_4x4" in payload
    assert "detections_5x5" in payload
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


def test_includes_distance_when_camera_info_available(monkeypatch):
    import camera.aruco_reader as ar

    if getattr(ar, "np", None) is None:
        pytest.skip("numpy not available; distance estimation disabled")

    monkeypatch.setattr(ar, "CvBridge", FakeBridge)

    if not hasattr(ar.cv2, "aruco"):
        monkeypatch.setattr(ar.cv2, "aruco", FakeAruco, raising=False)

    ar.cv2.aruco = FakeAruco

    det_4x4 = FakeDetector(FakeIds([42]), corners=[object()])
    det_5x5 = FakeDetector(None)

    detectors = [det_4x4, det_5x5]

    def fake_create_detector(_dictionary, _params):
        return detectors.pop(0)

    monkeypatch.setattr(ar, "_create_aruco_detector", fake_create_detector)

    def fake_estimate_pose(_corners, _marker_size, _camera_matrix, _dist_coeffs):
        tvecs = ar.np.array([[[0.0, 0.0, 0.61]]], dtype=float)
        return (None, tvecs, None)

    monkeypatch.setattr(
        ar.cv2.aruco,
        "estimatePoseSingleMarkers",
        fake_estimate_pose,
        raising=False,
    )

    node = ar.ArucoReader()

    cam_info = CameraInfo()
    cam_info.k = [
        600.0,
        0.0,
        320.0,
        0.0,
        600.0,
        240.0,
        0.0,
        0.0,
        1.0,
    ]
    cam_info.d = [0.0, 0.0, 0.0, 0.0, 0.0]
    node._camera_info_callback(cam_info)

    received = []
    listener = rclpy.create_node("aruco_detections_listener_distance")

    def cb(msg: String):
        received.append(msg.data)

    listener.create_subscription(String, "aruco_detections", cb, 10)

    node.listener_callback(_make_compressed_image())
    rclpy.spin_once(listener, timeout_sec=0.2)

    assert len(received) == 1
    payload = json.loads(received[0])
    assert payload["has_camera_info"] is True
    assert payload["ids_4x4"] == [42]
    assert payload["detections_4x4"][0]["id"] == 42
    assert payload["detections_4x4"][0]["z_m"] == pytest.approx(0.61)

    node.destroy_node()
    listener.destroy_node()
