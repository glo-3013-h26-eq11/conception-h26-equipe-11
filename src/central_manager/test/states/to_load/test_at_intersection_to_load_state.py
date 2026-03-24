import pytest
from unittest.mock import patch, MagicMock

from central_manager.states.to_load.at_intersection_to_load_state import (
    AtIntersectionToLoadState,
)
from central_manager.states.node_action_enum import NodeAction


@pytest.fixture
def blackboard_mock():
    logger_mock = MagicMock()
    node_mock = MagicMock()
    node_mock.get_logger.return_value = logger_mock

    return {"node": node_mock, "enforcers": []}


@pytest.mark.parametrize(
    "node_action, expected_outcome",
    [
        (NodeAction.LEFT_TURN, "left_turn"),
        (NodeAction.FORWARD_TURN, "forward_turn"),
        (NodeAction.RIGHT_TURN, "right_turn"),
        (NodeAction.WAIT_LOAD_ZONE, "wait_load_zone"),
    ],
)
def test_at_intersection_to_load_state_outcomes(
    blackboard_mock, node_action, expected_outcome
):
    state = AtIntersectionToLoadState(blackboard_mock["node"])

    with patch.object(state, "get_current_node_action", return_value=node_action):
        outcome = state.execute(blackboard_mock)

    assert outcome == expected_outcome
    assert len(blackboard_mock["enforcers"]) == 1


def test_invalid_node_action_logs_error(blackboard_mock):
    state = AtIntersectionToLoadState(blackboard_mock["node"])

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
    state = AtIntersectionToLoadState(blackboard_mock["node"])

    with patch.object(
        state,
        "get_current_node_action",
        return_value=NodeAction.LEFT_TURN,
    ):
        outcome = state.execute(blackboard_mock)

    assert outcome == "left_turn"
