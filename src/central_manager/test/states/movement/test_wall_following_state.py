import threading
import time
import pytest
import rclpy

from std_msgs.msg import String
from rclpy.node import Node

from central_manager.states.movement.wall_following_state import (
    WallFollowingState,
)
import json


@pytest.fixture(scope="module")
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_wall_following_positioning_transitions_to_current_node_load(rclpy_init):
    node = Node("test_wall_following_positioning_node")
    state = WallFollowingState(node)

    blackboard = {"node": node, "enforcers": ["dummy"], "route_mode": "load"}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(String, "current_node", 10)
    data = {"distance": 5}
    msg = String(data=json.dumps(data))
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "current_node_load"
    assert len(blackboard["enforcers"]) == 1  # we switch to immobile pending intersection handling

    node.destroy_node()


def test_wall_following_positioning_transitions_to_current_node_deposit(rclpy_init):
    node = Node("test_wall_following_positioning_node_deposit")
    state = WallFollowingState(node)

    blackboard = {"node": node, "enforcers": ["dummy"], "route_mode": "deposit"}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(String, "current_node", 10)
    data = {"distance": 5}
    msg = String(data=json.dumps(data))
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "current_node_deposit"
    assert len(blackboard["enforcers"]) == 1

    node.destroy_node()
