from central_manager.enforcer_manager_node import EnforcerManagerNode
import pytest
import rclpy


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
