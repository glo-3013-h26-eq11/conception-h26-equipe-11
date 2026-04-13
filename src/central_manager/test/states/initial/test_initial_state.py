import pytest
import rclpy
from std_msgs.msg import Bool
from rclpy.node import Node
from unittest.mock import MagicMock

from central_manager.states.initial.initial_state import InitialState
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


@pytest.fixture(scope="module", autouse=True)
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_initial_state_transitions_to_system_ready():
    node = Node("test_initial_state_node")
    state = InitialState(node)
    state.home_deposit_zone = 8
    state.home_deposit_zone_pub = MagicMock()

    blackboard = {"node": node, BLACKBOARD_ENFORCERS: []}
    state.on_enter(blackboard)

    state.rover_start_callback(Bool(data=True))
    outcome = state.step(blackboard)

    assert outcome == "system_ready"
    assert len(blackboard[BLACKBOARD_ENFORCERS]) == 1

    node.destroy_node()
