import threading
import time
import pytest
import rclpy

from std_msgs.msg import String, Bool
from rclpy.node import Node

from central_manager.states.to_deposit.at_deposit_zone_to_deposit_state import (
    AtDepositZoneToDeposit,
)
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


@pytest.fixture(scope="module", autouse=True)
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture()
def state():
    node = Node("node")
    s = AtDepositZoneToDeposit(node)
    yield s
    node.destroy_node()


def test_at_deposit_zone_to_deposit_state_transitions_to_deposit_over(state):
    blackboard = {BLACKBOARD_ENFORCERS: []}
    outcome_holder = {}

    def run_state():
        outcome_holder["outcome"] = state.execute(blackboard)

    thread = threading.Thread(target=run_state)
    thread.start()

    time.sleep(0.2)

    pub = state.node.create_publisher(String, "deposit_over", 10)
    msg = String(data="done")
    pub.publish(msg)

    thread.join(timeout=2.0)

    assert outcome_holder.get("outcome") == "deposit_over"


def test_when_stop_rover_then_outcome_back_to_init(state):
    blackboard = {BLACKBOARD_ENFORCERS: []}
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
