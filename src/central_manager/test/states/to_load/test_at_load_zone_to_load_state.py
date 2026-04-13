import pytest
import rclpy
from std_msgs.msg import String, Bool
from rclpy.node import Node

from central_manager.states.to_load.at_load_zone_to_load_state import AtLoadZoneToLoad
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


@pytest.fixture(scope="module", autouse=True)
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture()
def state():
    node = Node("node")
    s = AtLoadZoneToLoad(node)
    yield s
    node.destroy_node()


def test_at_load_zone_to_load_state_transitions_to_load_over(state):
    blackboard = {BLACKBOARD_ENFORCERS: []}
    state.on_enter(blackboard)

    state.load_over_callback(String(data="done"))
    assert state.step(blackboard) == "load_over"


def test_when_stop_rover_then_outcome_back_to_init(state):
    blackboard = {BLACKBOARD_ENFORCERS: []}
    state.on_enter(blackboard)

    state.rover_stop_callback(Bool(data=False))
    assert state.step(blackboard) == "back_to_init"
