import pytest
import rclpy
from std_msgs.msg import String
from web_interface.system_health_node import HealthPingingNode
import time
import json


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def health_pinging_node():
    node = HealthPingingNode("node_name", "package_name")
    yield node
    node.destroy_node()


def test_when_ping_then_publish_node_status(health_pinging_node):
    received_msgs = []

    def capture_callback(msg):
        data = json.loads(msg.data)
        received_msgs.append(data)

    health_pinging_node.create_subscription(
        String, "/health/heartbeat", capture_callback, 10
    )

    start = time.time()
    while time.time() - start < 1.1:
        rclpy.spin_once(health_pinging_node, timeout_sec=0.1)

    assert len(received_msgs) >= 1
