from central_manager.enforcer_manager_node import EnforcerManagerNode
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
import pytest
import rclpy
import json


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    if not rclpy.ok():
        rclpy.init()
    yield
    if rclpy.ok():
        rclpy.shutdown()


@pytest.fixture
def node():
    enforcer_manager_node = EnforcerManagerNode()
    yield enforcer_manager_node
    enforcer_manager_node.destroy_node()
