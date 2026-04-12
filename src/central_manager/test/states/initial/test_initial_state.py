import threading
import time
import pytest
import rclpy

from std_msgs.msg import Bool
from rclpy.node import Node

from central_manager.states.initial.initial_state import InitialState
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS

from unittest.mock import MagicMock


@pytest.fixture(scope="module")
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_initial_state_transitions_to_system_ready(rclpy_init):
    node = Node("test_initial_state_node")
    state = InitialState(node)
    state.home_deposit_zone = 8
    state.home_deposit_zone_pub = MagicMock()

    blackboard = {"node": node, BLACKBOARD_ENFORCERS: []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(Bool, "rover/start", 10)
    msg = Bool(data=True)
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "system_ready"
    assert len(blackboard[BLACKBOARD_ENFORCERS]) == 1

    node.destroy_node()
