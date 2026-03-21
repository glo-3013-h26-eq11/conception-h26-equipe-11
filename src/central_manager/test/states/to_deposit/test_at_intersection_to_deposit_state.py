import pytest
from unittest.mock import patch

from central_manager.states.to_deposit.at_intersection_to_deposit_state import (
    AtIntersectionToDepositState,
)
from central_manager.states.node_action_enum import NodeAction


@pytest.fixture
def blackboard_mock():
    class FakeLogger:
        def info(self, msg):
            pass

        def error(self, msg):
            pass

    class FakeNode:
        def __init__(self):
            self.get_logger = lambda: FakeLogger()

    return {"node": FakeNode(), "enforcers": []}


@pytest.mark.parametrize(
    "node_action, expected_outcome",
    [
        (NodeAction.LEFT_TURN, "left_turn"),
        (NodeAction.FORWARD_TURN, "forward_turn"),
        (NodeAction.RIGHT_TURN, "right_turn"),
        (NodeAction.WAIT_DEPOSIT_ZONE, "wait_deposit_zone"),
    ],
)
def test_at_intersection_to_deposit_state_outcomes(
    blackboard_mock, node_action, expected_outcome
):
    state = AtIntersectionToDepositState(blackboard_mock["node"])

    with patch.object(state, "get_current_node_action", return_value=node_action):
        outcome = state.execute(blackboard_mock)

    assert outcome == expected_outcome


def test_invalid_node_action_logs_error(blackboard_mock):
    state = AtIntersectionToDepositState(blackboard_mock["node"])

    with patch.object(state, "get_current_node_action", return_value=None):
        outcome = state.execute(blackboard_mock)

    assert outcome is None
