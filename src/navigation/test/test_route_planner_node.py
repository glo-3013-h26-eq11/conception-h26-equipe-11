import pytest
import rclpy
from std_msgs.msg import String
import json
from navigation.route_planner_node import RoutePlannerNode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def route_planner_node():
    node = RoutePlannerNode()
    yield node
    node.destroy_node()


def test_node_initializes(route_planner_node):
    assert route_planner_node.route_selector is not None
    assert route_planner_node.current_node is None
    assert route_planner_node.goal_node is None


def test_current_node_callback_updates_state(route_planner_node):
    msg = String()
    msg.data = "A1"
    route_planner_node.current_node_callback(msg)
    assert route_planner_node.current_node == "A1"


def test_goal_node_callback_updates_state(route_planner_node):
    msg = String()
    msg.data = "ZC1"
    route_planner_node.goal_node_callback(msg)
    assert route_planner_node.goal_node == "ZC1"


def test_route_not_computed_when_current_node_missing(route_planner_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    route_planner_node.create_subscription(String, "route_plan", capture_callback, 10)

    goal_msg = String()
    goal_msg.data = "ZC1"
    route_planner_node.goal_node_callback(goal_msg)

    rclpy.spin_once(route_planner_node, timeout_sec=0.1)

    assert len(received_msgs) == 0


def test_route_not_computed_when_goal_node_missing(route_planner_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    route_planner_node.create_subscription(String, "route_plan", capture_callback, 10)

    current_msg = String()
    current_msg.data = "A1"
    route_planner_node.current_node_callback(current_msg)

    rclpy.spin_once(route_planner_node, timeout_sec=0.1)

    assert len(received_msgs) == 0


def test_route_computed_and_published(route_planner_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    route_planner_node.create_subscription(String, "route_plan", capture_callback, 10)

    current_msg = String()
    current_msg.data = "A1"
    route_planner_node.current_node_callback(current_msg)

    goal_msg = String()
    goal_msg.data = "ZC1"
    route_planner_node.goal_node_callback(goal_msg)

    rclpy.spin_once(route_planner_node, timeout_sec=0.1)

    assert len(received_msgs) == 1
    route = json.loads(received_msgs[0])
    assert isinstance(route, list)
    assert len(route) >= 0


def test_route_valid_path(route_planner_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    route_planner_node.create_subscription(String, "route_plan", capture_callback, 10)

    current_msg = String()
    current_msg.data = "ZC1"
    route_planner_node.current_node_callback(current_msg)

    goal_msg = String()
    goal_msg.data = "ZD1"
    route_planner_node.goal_node_callback(goal_msg)

    rclpy.spin_once(route_planner_node, timeout_sec=0.1)

    assert len(received_msgs) == 1
    route = json.loads(received_msgs[0])
    assert isinstance(route, list)

    current = "ZC1"
    graph = route_planner_node.route_selector.graph
    for direction in route:
        assert direction in graph[current]
        current = graph[current][direction]
    assert current == "ZD1"


def test_route_not_published_for_invalid_nodes(route_planner_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    route_planner_node.create_subscription(String, "route_plan", capture_callback, 10)

    current_msg = String()
    current_msg.data = "INVALID"
    route_planner_node.current_node_callback(current_msg)

    goal_msg = String()
    goal_msg.data = "ZC1"
    route_planner_node.goal_node_callback(goal_msg)

    rclpy.spin_once(route_planner_node, timeout_sec=0.1)

    assert len(received_msgs) == 0
