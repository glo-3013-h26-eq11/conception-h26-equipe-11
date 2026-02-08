import json
import pytest
import rclpy
from std_msgs.msg import String
from navigation.route_planner_node import RoutePlannerNode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    route_planner_node = RoutePlannerNode()
    yield route_planner_node
    route_planner_node.destroy_node()


def _capture_topic_once(node, topic_name: str, timeout_sec: float = 0.2):
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, topic_name, cb, 10)
    rclpy.spin_once(node, timeout_sec=timeout_sec)
    return received


def test_does_not_publish_when_current_node_missing(node):
    goal_msg = String()
    goal_msg.data = "ZC1"

    node.goal_node_callback(goal_msg)
    received = _capture_topic_once(node, "route_plan")

    assert received == []


def test_does_not_publish_when_goal_node_missing(node):
    current_msg = String()
    current_msg.data = "A1"

    node.current_node_callback(current_msg)
    received = _capture_topic_once(node, "route_plan")

    assert received == []


def test_publishes_route_when_both_nodes_present(node):
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, "route_plan", cb, 10)

    current_msg = String()
    current_msg.data = "A1"
    goal_msg = String()
    goal_msg.data = "ZC1"

    node.current_node_callback(current_msg)
    node.goal_node_callback(goal_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    assert len(received) == 1
    route = json.loads(received[0])
    assert isinstance(route, list)


def test_does_not_publish_when_route_not_found(node):
    received = []

    def cb(msg: String):
        received.append(msg.data)

    node.create_subscription(String, "route_plan", cb, 10)

    current_msg = String()
    current_msg.data = "INVALID"
    goal_msg = String()
    goal_msg.data = "ZC1"

    node.current_node_callback(current_msg)
    node.goal_node_callback(goal_msg)
    rclpy.spin_once(node, timeout_sec=0.2)

    assert received == []
