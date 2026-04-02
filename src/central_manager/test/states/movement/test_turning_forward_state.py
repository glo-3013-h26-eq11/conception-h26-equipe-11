import threading
import time
import pytest
import rclpy
from std_msgs.msg import String, Bool
from rclpy.node import Node
from unittest.mock import Mock

from central_manager.states.movement.turning_forward_state import (
    TurningForwardState,
)
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS

DISTANCE = 0.3


@pytest.fixture(scope="module", autouse=True)
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture()
def state():
    node = Node("node")
    s = TurningForwardState(node)
    yield s
    node.destroy_node()


def test_when_turn_over_then_outcome_turn_over(state):
    blackboard = {BLACKBOARD_ENFORCERS: []}
    outcome_holder = {}
    state.intersection_filter_pause_publisher = Mock()

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = state.node.create_publisher(String, "turn_over", 10)
    msg = String(data="done")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "turn_over"
    state.intersection_filter_pause_publisher.publish.assert_called_once()


def test_when_stop_rover_then_outcome_back_to_init(state):
    blackboard = {BLACKBOARD_ENFORCERS: []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = state.node.create_publisher(Bool, "rover/start", 10)
    msg = Bool(data=False)
    pub.publish(msg)

    time.sleep(0.2)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "back_to_init"


def test_when_turn_over_received_while_state_is_inactive_then_ignore_message(state):
    state.intersection_filter_pause_publisher = Mock()

    state.turn_over_callback(String(data="done"))

    assert state.outcome is None
    state.intersection_filter_pause_publisher.publish.assert_not_called()
