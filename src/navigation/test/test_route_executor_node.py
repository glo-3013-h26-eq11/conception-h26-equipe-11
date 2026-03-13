import json

import pytest
import rclpy
from geometry_msgs.msg import Twist
from std_msgs.msg import String

from navigation.route_executor_node import RouteExecutorNode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    route_executor = RouteExecutorNode()
    yield route_executor
    route_executor.destroy_node()


def test_given_no_override_when_wall_cmd_received_then_publish_wall_cmd(node):
    received = []

    def call_back(msg):
        received.append((msg.linear.x, msg.angular.z))

    node.create_subscription(Twist, "/cmd_vel", call_back, 10)

    wall_cmd = Twist()
    wall_cmd.linear.x = 0.4
    wall_cmd.angular.z = 0.1

    node.wall_cmd_callback(wall_cmd)
    rclpy.spin_once(node, timeout_sec=0.1)

    assert received == [(0.4, 0.1)]


def test_given_route_and_current_node_when_left_turn_needed_then_override_cmd(node):
    node.route_nodes_callback(String(data=json.dumps(["A1", "A2"])))
    node.route_directions_callback(String(data=json.dumps(["g"])))

    current_node_msg = String()
    current_node_msg.data = "A1"
    node.current_node_callback(current_node_msg)

    assert node._is_override_active() is True
    assert node.override_cmd.linear.x > 0.0
    assert node.override_cmd.angular.z > 0.0
