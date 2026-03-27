import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from central_manager.enforcer_manager_node import EnforcerManagerNode
from unittest.mock import MagicMock
from geometry_msgs.msg import Twist
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS
import time


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    if not rclpy.ok():
        rclpy.init()
    yield
    if rclpy.ok():
        rclpy.shutdown()


@pytest.fixture()
def node_no_publisher():
    node = EnforcerManagerNode()
    node.pub_cmd_vel_safe = MagicMock()
    yield node
    node.destroy_node()


@pytest.fixture()
def node():
    node = EnforcerManagerNode()
    yield node
    node.destroy_node()


def test_when_cmd_callback_then_enforce_command_and_update_real_speed_and_publish_safe(
    node_no_publisher,
):

    # Arrange
    e1 = MagicMock()
    e2 = MagicMock()

    cmd_in = Twist()
    cmd_in.linear.x = 1.0

    cmd_after_e1 = Twist()
    cmd_after_e1.linear.x = 2.0

    cmd_after_e2 = Twist()
    cmd_after_e2.linear.x = 3.0

    e1.enforce_cmd.return_value = cmd_after_e1
    e2.enforce_cmd.return_value = cmd_after_e2

    node_no_publisher.blackboard[BLACKBOARD_ENFORCERS] = [e1, e2]

    # Act
    node_no_publisher.cmd_callback(cmd_in)

    # Assert
    e1.enforce_cmd.assert_called_once_with(cmd_in)
    e2.enforce_cmd.assert_called_once_with(cmd_after_e1)

    e1.update_with_real_speed.assert_called_once_with(cmd_after_e2)
    e2.update_with_real_speed.assert_called_once_with(cmd_after_e2)

    node_no_publisher.pub_cmd_vel_safe.publish.assert_called_once_with(cmd_after_e2)


def test_when_receives_cmd_vel_then_publishes_cmd_vel_safe(node):

    received = []

    def cb(msg: Twist):
        received.append(received)

    publisher_cmd_vel = node.create_publisher(Twist, "/cmd_vel", 10)
    node.create_subscription(Twist, "/cmd_vel_safe", cb, 10)

    for _ in range(5):
        rclpy.spin_once(node, timeout_sec=0.05)

    cmd_in = Twist()

    publisher_cmd_vel.publish(cmd_in)

    executor = SingleThreadedExecutor()
    executor.add_node(node)

    start = time.time()
    while time.time() - start < 2.0:
        executor.spin_once(timeout_sec=0.1)

    assert len(received) == 1
