import json
import sys
import types
import importlib

import pytest
import rclpy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from camera.aruco_reader_node import CAMERA_OFFSET


def _install_fake_modules(
    monkeypatch, *, ids_4x4, ids_5x5, depth_value=0.42, tag_angle=0
):
    import numpy as np

    cv_bridge_mod = types.ModuleType("cv_bridge")

    class _FakeBridge:
        def imgmsg_to_cv2(self, _msg, desired_encoding="bgr8"):
            return object()

    cv_bridge_mod.CvBridge = _FakeBridge

    cv2_mod = types.ModuleType("cv2")

    class _FakeAruco:
        DICT_4X4_50 = object()
        DICT_5X5_50 = object()

        @staticmethod
        def getPredefinedDictionary(which):
            return which

        @staticmethod
        def DetectorParameters_create():
            return object()

        @staticmethod
        def detectMarkers(_frame, dictionary, parameters=None):
            del parameters
            if dictionary is _FakeAruco.DICT_4X4_50:
                if ids_4x4 is None:
                    ids = None
                else:
                    ids = np.array(ids_4x4, dtype=np.int32).reshape(-1, 1)
            elif dictionary is _FakeAruco.DICT_5X5_50:
                if ids_5x5 is None:
                    ids = None
                else:
                    ids = np.array(ids_5x5, dtype=np.int32).reshape(-1, 1)
            else:
                ids = None

            corners = []
            if ids is not None:
                corners = [object() for _ in range(int(ids.shape[0]))]
            return corners, ids, []

        @staticmethod
        def estimatePoseSingleMarkers(_corners, _marker_size, _mtx, _dist):
            tvecs = np.array(
                [[[0.0, 0.0, float(depth_value)]]],
                dtype=np.float32,
            )
            rvecs = np.array(
                [[[0.0, 0.0, float(tag_angle)]]],
                dtype=np.float32,
            )
            return rvecs, tvecs, None

    cv2_mod.aruco = _FakeAruco

    depthai_mod = types.ModuleType("depthai")

    class _FakeCameraBoardSocket:
        RGB = object()

    class _FakeCalibration:
        def getCameraIntrinsics(self, _socket, _w, _h):
            return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

        def getDistortionCoefficients(self, _socket):
            return [0.0, 0.0, 0.0, 0.0, 0.0]

    class _FakeDevice:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def readCalibration(self):
            return _FakeCalibration()

    depthai_mod.Device = _FakeDevice
    depthai_mod.CameraBoardSocket = _FakeCameraBoardSocket

    monkeypatch.setitem(sys.modules, "cv_bridge", cv_bridge_mod)
    monkeypatch.setitem(sys.modules, "cv2", cv2_mod)
    monkeypatch.setitem(sys.modules, "depthai", depthai_mod)

    sys.modules.pop("camera.aruco_reader_node", None)
    return importlib.import_module("camera.aruco_reader_node")


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


def _make_compressed_image(frame_id="oak", sec=1, nanosec=2):
    msg = Image()
    msg.header.frame_id = frame_id
    msg.header.stamp.sec = sec
    msg.header.stamp.nanosec = nanosec
    return msg


def test_publishes_ids_when_detected(monkeypatch):
    ar = _install_fake_modules(
        monkeypatch, ids_4x4=[1, 2], ids_5x5=[10], depth_value=0.5, tag_angle=0
    )

    node = ar.ArucoReaderNode()

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
    assert payload["ids_5x5"] == [10]
    assert "v" not in payload
    assert payload["stamp"]["sec"] == 123
    assert payload["stamp"]["nanosec"] == 456
    assert payload["markers_4x4"] == [
        {
            "tag": 1,
            "depth": 0.50 + CAMERA_OFFSET,
            "angle_x_deg": pytest.approx(0.0),
            "z_forward": 0.5,
            "tag_angle": pytest.approx(0),
        },
        {
            "tag": 2,
            "depth": 0.50 + CAMERA_OFFSET,
            "angle_x_deg": pytest.approx(0),
            "z_forward": 0.5,
            "tag_angle": pytest.approx(0),
        },
    ]
    assert payload["markers_5x5"] == [
        {
            "tag": 10,
            "depth": 0.50 + CAMERA_OFFSET,
            "angle_x_deg": pytest.approx(0.0),
            "z_forward": pytest.approx(0.5),
            "tag_angle": pytest.approx(0),
        }
    ]

    node.destroy_node()
    listener.destroy_node()


def test_does_not_publish_when_no_detections(monkeypatch):
    ar = _install_fake_modules(monkeypatch, ids_4x4=None, ids_5x5=None)

    node = ar.ArucoReaderNode()

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
