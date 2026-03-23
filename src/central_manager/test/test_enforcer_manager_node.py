from central_manager.enforcer_manager_node import EnforcerManagerNode
import pytest
import rclpy
import unitt

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
    enforcer_manager_node.pub_cmd_vel_safe = 
    yield enforcer_manager_node
    enforcer_manager_node.destroy_node()


def test_when_cmd_callback_then_enforce_all_enforcers(node):
    pass
