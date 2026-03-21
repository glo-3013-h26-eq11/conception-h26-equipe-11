import threading
import time
import pytest
import rclpy

from std_msgs.msg import String
from rclpy.node import Node

from central_manager.states.movement.turning_left_state import (
    TurningLeftState,
)


@pytest.fixture(scope="module")
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_turning_left_to_load_state_transitions_to_turn_over(rclpy_init):
    node = Node("test_turning_left_to_load_node")
    state = TurningLeftState(node)

    blackboard = {"node": node, "enforcers": []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(String, "turn_over", 10)
    msg = String(data="done")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "turn_over"

    node.destroy_node()
