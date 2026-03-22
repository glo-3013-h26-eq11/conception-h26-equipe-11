import threading
import time
import pytest
import rclpy

from std_msgs.msg import String
from rclpy.node import Node

from central_manager.states.to_deposit.at_deposit_zone_to_deposit_state import (
    AtDepositZoneToDeposit,
)


@pytest.fixture(scope="module")
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_at_deposit_zone_to_deposit_state_transitions_to_deposit_over(rclpy_init):
    node = Node("test_at_deposit_zone_to_deposit_node")
    state = AtDepositZoneToDeposit(node)

    blackboard = {"node": node, "enforcers": []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = node.create_publisher(String, "deposit_over", 10)
    msg = String(data="done")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "deposit_over"

    node.destroy_node()
