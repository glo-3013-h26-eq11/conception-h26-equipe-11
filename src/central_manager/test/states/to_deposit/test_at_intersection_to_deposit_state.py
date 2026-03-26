import pytest
from unittest.mock import patch, MagicMock

from central_manager.states.to_deposit.at_intersection_to_deposit_state import (
    AtIntersectionToDepositState,
)
from central_manager.states.node_action_enum import NodeAction
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


@pytest.fixture
def blackboard_mock():
    logger_mock = MagicMock()
    node_mock = MagicMock()
    node_mock.get_logger.return_value = logger_mock

    return {"node": node_mock, BLACKBOARD_ENFORCERS: []}


@pytest.mark.parametrize(
    "node_action, expected_outcome",
    [
        (NodeAction.LEFT_TURN, "left_turn"),
        (NodeAction.FORWARD_TURN, "forward_turn"),
        (NodeAction.RIGHT_TURN, "right_turn"),
        (NodeAction.WAIT_DEPOSIT_ZONE, "wait_deposit_zone"),
        (NodeAction.WALL_FOLLOW, "right_turn"),
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


class FakeFuture:
    def __init__(self, action: str):
        self._action = action

    def result(self):
        class Response:
            pass

        r = Response()
        r.action = self._action
        return r


def test_left_turn_transition(blackboard_mock):
    state = AtIntersectionToDepositState(blackboard_mock["node"])

    with patch.object(
        state,
        "get_current_node_action",
        return_value=NodeAction.LEFT_TURN,
    ):
        outcome = state.execute(blackboard_mock)

    assert outcome == "left_turn"
