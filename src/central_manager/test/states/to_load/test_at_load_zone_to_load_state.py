import threading
import time
import pytest
import rclpy

from std_msgs.msg import String
from rclpy.node import Node

from central_manager.states.to_load.at_load_zone_to_load_state import AtLoadZoneToLoad


@pytest.fixture(scope="module")
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_at_load_zone_to_load_state_transitions_to_load_over(rclpy_init):
    node = Node("test_at_load_zone_to_load_node")
    state = AtLoadZoneToLoad(node)

    blackboard = {"node": node, "enforcers": []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(String, "load_over", 10)
    msg = String(data="done")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "load_over"

    node.destroy_node()
