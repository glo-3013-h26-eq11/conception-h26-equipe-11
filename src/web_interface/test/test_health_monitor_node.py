import pytest
import rclpy
from std_msgs.msg import String
from web_interface.system_health_node import HealthMonitorNode
import time
import json

@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def health_monitor_node():
    node = HealthMonitorNode()
    yield node
    node.destroy_node()


def test_when_ping_with_node_status_then_publish_data_structure(health_monitor_node):
    received_msgs = []

    def capture_callback(msg):
        data = json.loads(msg.data)
        received_msgs.append(data)

    health_monitor_node.create_subscription(String, "/health_status", capture_callback, 10)
    
    start = time.time()
    while time.time() - start < 1.1:
        rclpy.spin_once(health_monitor_node, timeout_sec=0.1)

    expected = {
        "web_interface":{
            "health_monitor": "ACTIVE"
        }
    }

    assert len(received_msgs) == 1
    assert received_msgs[0] == expected
    
    
def test_when_ping_then_fails_to_ping_for_3_sec_then_publish_crashed(health_monitor_node):
    received_msgs = []

    def capture_callback(msg):
        data = json.loads(msg.data)
        received_msgs.append(data)

    publisher = health_monitor_node.create_publisher(String, "/health/heartbeat", 10)

    health_monitor_node.create_subscription(String, "/health_status", capture_callback, 10)
    
    input_payload = String()
    input_payload.data = json.dumps({
        "name": "node_name",
        "system": "package_name",
        "status" : "ACTIVE"
    })
    
    publisher.publish(input_payload)
    
    start = time.time()
    while time.time() - start < 4:
        rclpy.spin_once(health_monitor_node, timeout_sec=0.1)

    assert received_msgs[-1]["package_name"]["node_name"] == "CRASHED"