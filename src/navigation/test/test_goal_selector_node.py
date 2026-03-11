import json

import pytest
import rclpy
from std_msgs.msg import String

from navigation.goal_selector_node import GoalSelectorNode

TEST_GRAPH = {
    "A1": {"left": "ZC1", "straight": "B1", "right": "ZD1"},
    "B1": {"left": None, "straight": "ZC2", "right": None},
    "ZC1": {"left": None, "straight": None, "right": None},
    "ZC2": {"left": None, "straight": None, "right": None},
    "ZD1": {"left": None, "straight": None, "right": None},
}


@pytest.fixture(scope="module", autouse=True)
def ros():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def node():
    n = GoalSelectorNode()
    yield n
    n.destroy_node()


def msg(data: str) -> String:
    m = String()
    m.data = data
    return m


def publish_inputs(
    node: GoalSelectorNode,
    *,
    graph=None,
    current=None,
    goals=None,
    mode=None,
):
    if current is not None:
        node._current_callback(msg(current))
    if goals is not None:
        node._available_goals_callback(
            msg(json.dumps(goals) if isinstance(goals, list) else goals)
        )
    if mode is not None:
        node._goal_mode_callback(msg(mode))
    if graph is not None:
        node._map_callback(msg(json.dumps(graph)))


def subscribe_goal(node: GoalSelectorNode):
    received = []
    node.create_subscription(String, "goal_node", lambda m: received.append(m.data), 10)
    return received


def test_given_load_mode_when_all_inputs_are_received_then_publishes_best_load_goal(
    node,
):
    # Arrange
    received = subscribe_goal(node)

    # Act
    publish_inputs(
        node,
        graph=TEST_GRAPH,
        current="A1",
        goals=["ZC1", "ZC2", "ZD1"],
        mode="GO_LOAD",
    )
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received[-1] == "ZC1"


def test_given_drop_mode_when_all_inputs_are_received_then_publishes_best_drop_goal(
    node,
):
    # Arrange
    received = subscribe_goal(node)

    # Act
    publish_inputs(
        node,
        graph=TEST_GRAPH,
        current="A1",
        goals=["ZC1", "ZC2", "ZD1"],
        mode="GO_DROP",
    )
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received[-1] == "ZD1"


def test_given_no_current_node_when_other_inputs_are_received_then_does_not_publish(
    node,
):
    # Arrange
    received = subscribe_goal(node)

    # Act
    publish_inputs(
        node,
        graph=TEST_GRAPH,
        goals=["ZC1", "ZC2", "ZD1"],
        mode="GO_LOAD",
    )
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received == []


def test_given_invalid_goal_mode_when_other_inputs_are_received_then_does_not_publish(
    node,
):
    # Arrange
    received = subscribe_goal(node)

    # Act
    publish_inputs(
        node,
        graph=TEST_GRAPH,
        current="A1",
        goals=["ZC1", "ZC2", "ZD1"],
        mode="INVALID",
    )
    rclpy.spin_once(node, timeout_sec=0.2)

    # Assert
    assert received == []
