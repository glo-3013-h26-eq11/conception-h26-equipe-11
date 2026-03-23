import threading
import time
import pytest
import rclpy

from std_msgs.msg import String
from rclpy.node import Node

from central_manager.states.movement.wall_following_state import (
    WallFollowingState,
)


@pytest.fixture(scope="module")
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_wall_following_positioning_transitions_to_current_node(rclpy_init):
    node = Node("test_wall_following_positioning_node")
    state = WallFollowingState(node)

    blackboard = {"node": node, "enforcers": ["dummy"]}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(String, "current_node", 10)
    msg = String(data="aruco_12")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "current_node"
    assert len(blackboard["enforcers"]) == 2

    node.destroy_node()
