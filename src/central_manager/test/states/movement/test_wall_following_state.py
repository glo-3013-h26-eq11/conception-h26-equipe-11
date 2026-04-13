import threading
import time
import pytest
import rclpy

from std_msgs.msg import String, Bool
from rclpy.node import Node

from central_manager.states.movement.wall_following_state import (
    WallFollowingState,
)
import json
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


def test_when_stop_over_and_current_node_then_transitions(state):
    blackboard = {BLACKBOARD_ENFORCERS: [], BLACKBOARD_PREVIOUS_STOP_TAG: None}
    outcome_holder = {}

    state.get_is_the_intersection_valid_to_stop = lambda x: x == x

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = state.node.create_publisher(String, "current_node", 10)
    pub_stop_over = state.node.create_publisher(Bool, "stop_over", 10)

    data = {"distance": 5, "angle": 0.0, "tag": 1}
    msg = String(data=json.dumps(data))
    pub.publish(msg)

    data_stop_over = Bool()
    data_stop_over.data = False
    pub_stop_over.publish(data_stop_over)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "current_node"
    assert len(blackboard[BLACKBOARD_ENFORCERS]) == 2
