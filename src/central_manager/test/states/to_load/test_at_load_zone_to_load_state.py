import threading
import time
import pytest
import rclpy

from std_msgs.msg import String, Bool
from rclpy.node import Node

from central_manager.states.to_load.at_load_zone_to_load_state import AtLoadZoneToLoad


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
    blackboard = {"node": state.node, "enforcers": []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = state.node.create_publisher(String, "load_over", 10)
    msg = String(data="done")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "load_over"


def test_when_stop_rover_then_outcome_back_to_init(state):
    blackboard = {"node": state.node, "enforcers": []}
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
