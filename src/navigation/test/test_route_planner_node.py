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


def test_given_current_only_when_received_then_publishes_nodes(node):
    # Arrange
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    current_msg = String()
    current_msg.data = "A1"

    # Act
    node.current_node_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received
    assert json.loads(received[0]) == ["A1", "ZC1"]


def test_given_current_only_when_received_then_publishes_directions(node):
    # Arrange
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, "route_plan/directions", cb, 10)

    current_msg = String()
    current_msg.data = "A1"

    # Act
    node.current_node_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert json.loads(received[0]) == ["left"]


def test_given_goal_mode_drop_when_current_received_then_publishes_drop_route(node):
    # Arrange
    received = []

    def cb(msg: String):
        received.append(json.loads(msg.data))

    node.create_subscription(String, "route_plan/nodes", cb, 10)

    current_msg = String()
    current_msg.data = "A1"
    goal_mode_msg = String()
    goal_mode_msg.data = "GO_DROP"

    # Act
    node.goal_mode_callback(goal_mode_msg)
    node.current_node_callback(current_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received[0][-1] == "ZD1"


def test_given_load_service_when_path_exists_then_returns_first_direction_action(node):
    # Arrange
    node.current_node = "A1"

    # Act
    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    # Assert
    assert response.action == "left"


def test_given_deposit_service_when_path_exists_then_returns_first_direction_action(
    node,
):
    # Arrange
    node.current_node = "A1"

    # Act
    response = node.handle_get_node_action_deposit(None, type("Resp", (), {})())

    # Assert
    assert response.action == "right"


def test_given_load_service_when_at_goal_then_returns_wait_load_action(node):
    # Arrange
    node.current_node = "ZC1"
    node.available_goals = ["ZC1", "ZD1"]

    # Act
    response = node.handle_get_node_action_load(None, type("Resp", (), {})())

    # Assert
    assert response.action == "load"
