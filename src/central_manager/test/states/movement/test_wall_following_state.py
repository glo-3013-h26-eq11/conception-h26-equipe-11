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


def test_wall_following_positioning_transitions_to_current_node(state):
    blackboard = {"node": state.node, "enforcers": ["dummy"]}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = state.node.create_publisher(String, "current_node", 10)
    data = {"distance": 5}
    msg = String(data=json.dumps(data))
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "current_node"
    assert len(blackboard["enforcers"]) == 2


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
