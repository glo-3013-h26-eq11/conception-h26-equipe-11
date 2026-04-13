import json

import pytest
import rclpy
from std_msgs.msg import String, Bool
from rclpy.node import Node

from central_manager.states.movement.wall_following_state import WallFollowingState
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)


@pytest.fixture(scope="module", autouse=True)
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture()
def state():
    node = Node("node")
    s = WallFollowingState(node)
    yield s
    node.destroy_node()


def test_when_rover_stop_then_outcome_back_to_init(state):
    blackboard = {BLACKBOARD_ENFORCERS: [], BLACKBOARD_PREVIOUS_STOP_TAG: None}
    state.on_enter(blackboard)

    state.rover_stop_callback(Bool(data=False))
    assert state.step(blackboard) == "back_to_init"


def test_when_stop_over_and_current_node_then_transitions(state):
    blackboard = {BLACKBOARD_ENFORCERS: [], BLACKBOARD_PREVIOUS_STOP_TAG: None}
    state.on_enter(blackboard)
    state.get_is_the_intersection_valid_to_stop = lambda x: x == x

    data = {"distance": 5, "angle": 0.0, "tag": 1}
    state.at_intersection_callback(String(data=json.dumps(data)))
    state.stop_over(Bool(data=False))

    assert state.step(blackboard) == "current_node"
    assert len(blackboard[BLACKBOARD_ENFORCERS]) == 2


def test_when_current_node_and_is_not_valid_stop_then_previous_tag_is_aruco_tag(state):
    blackboard = {BLACKBOARD_ENFORCERS: [], BLACKBOARD_PREVIOUS_STOP_TAG: None}
    ARUCO_TAG = 1

    class FakeFuture:
        def __init__(self, result):
            self._result = result

        def result(self):
            return self._result

    class FakeResponse:
        def __init__(self, is_valid):
            self.is_valid = is_valid

    fake_result = FakeResponse(is_valid=False)
    fake_future = FakeFuture(fake_result)

    state.on_enter(blackboard)
    state.get_is_the_intersection_valid_to_stop = (
        lambda x: state.handle_get_is_the_intersection_valid_to_stop(x, fake_future)
    )

    data = {"distance": 5, "angle": 0.0, "tag": ARUCO_TAG}
    state.at_intersection_callback(String(data=json.dumps(data)))

    assert state.previous_tag == ARUCO_TAG
