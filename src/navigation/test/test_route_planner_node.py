import json
import pytest
import rclpy
from std_msgs.msg import String

from navigation.route_planner_node import RoutePlannerNode
from navigation.route_selector import RouteSelector


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    # Arrange: Map format (left, straight, right)
    temp_graph = {
        "A1": {"left": "ZC1", "straight": "A4", "right": "ZD1"},
        "A2": {"left": "A4", "straight": "ZD1", "right": "A2"},
        "A3": {"left": "ZD1", "straight": "A2", "right": "ZC1"},
        "A4": {"left": "A2", "straight": "ZC1", "right": "A4"},
        "ZC1": {"straight": "A1"},
        "ZD1": {"straight": "A3"},
    }
    route_selector = RouteSelector(graph=temp_graph)
    route_planner_node = RoutePlannerNode(route_selector=route_selector)

    yield route_planner_node

    route_planner_node.destroy_node()


def _capture_topic_once(node, topic_name: str, timeout_sec: float = 0.2):
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, topic_name, cb, 10)
    rclpy.spin_once(node, timeout_sec=timeout_sec)
    return received


def test_given_goal_only_when_goal_received_then_does_not_publish_nodes(node):
    # Arrange
    goal_msg = String()
    goal_msg.data = "ZC1"

    # Act
    node.goal_node_callback(goal_msg)
    received = _capture_topic_once(node, "route_plan/nodes")

    # Assert
    assert received == []


def test_given_current_only_when_current_received_then_does_not_publish_nodes(node):
    # Arrange
    current_msg = String()
    current_msg.data = "A1"

    # Act
    node.current_node_callback(current_msg)
    received = _capture_topic_once(node, "route_plan/nodes")

    # Assert
    assert received == []


def test_given_goal_only_when_goal_received_then_does_not_publish_directions(node):
    # Arrange
    goal_msg = String()
    goal_msg.data = "ZC1"

    # Act
    node.goal_node_callback(goal_msg)
    received = _capture_topic_once(node, "route_plan/directions")

    # Assert
    assert received == []


def test_given_current_only_when_current_received_then_does_not_publish_directions(
    node,
):
    # Arrange
    current_msg = String()
    current_msg.data = "A1"

    # Act
    node.current_node_callback(current_msg)
    received = _capture_topic_once(node, "route_plan/directions")

    # Assert
    assert received == []


def test_given_both_nodes_set_when_goal_received_then_publishes_nodes_list(node):
    # Arrange
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    current_msg = String()
    current_msg.data = "A1"
    goal_msg = String()
    goal_msg.data = "ZC1"

    # Act
    node.current_node_callback(current_msg)
    node.goal_node_callback(goal_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received and json.loads(received[0]) != []


def test_given_both_nodes_set_when_goal_received_then_publishes_directions_list(node):
    # Arrange
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, "route_plan/directions", cb, 10)

    current_msg = String()
    current_msg.data = "A1"
    goal_msg = String()
    goal_msg.data = "ZC1"

    # Act
    node.current_node_callback(current_msg)
    node.goal_node_callback(goal_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received and json.loads(received[0]) != []


def test_given_invalid_start_node_when_goal_received_then_raises_value_error(node):
    # Arrange
    current_msg = String()
    current_msg.data = "INVALID"
    goal_msg = String()
    goal_msg.data = "ZC1"

    node.current_node_callback(current_msg)

    # Act, Assert
    with pytest.raises(ValueError, match="Unknown start node"):
        node.goal_node_callback(goal_msg)
