import pytest
from unittest.mock import MagicMock

from central_manager.states.to_deposit.at_intersection_to_deposit_state import (
    AtIntersectionToDepositState,
)
from central_manager.states.node_action_enum import NodeAction
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS


class FakeResponse:
    def __init__(self, action: str):
        self.action = action


class FakeFuture:
    def __init__(self, action: str):
        self._action = action

    def add_done_callback(self, callback):
        callback(self)

    def result(self):
        return FakeResponse(self._action)


@pytest.fixture
def blackboard_mock():
    logger_mock = MagicMock()
    node_mock = MagicMock()
    node_mock.get_logger.return_value = logger_mock
    client_mock = MagicMock()
    client_mock.wait_for_service.return_value = True
    node_mock.create_client.return_value = client_mock

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
    state.client.call_async.return_value = FakeFuture(node_action.value)

    state.on_enter(blackboard_mock)
    assert state.step(blackboard_mock) == expected_outcome
    assert len(blackboard_mock[BLACKBOARD_ENFORCERS]) == 1


def test_invalid_node_action_logs_error(blackboard_mock):
    state = AtIntersectionToDepositState(blackboard_mock["node"])
    state.client.call_async.return_value = FakeFuture("invalid")

    state.on_enter(blackboard_mock)
    assert state.step(blackboard_mock) == "back_to_init"


def test_left_turn_transition(blackboard_mock):
    state = AtIntersectionToDepositState(blackboard_mock["node"])
    state.client.call_async.return_value = FakeFuture(NodeAction.LEFT_TURN.value)

    state.on_enter(blackboard_mock)
    assert state.step(blackboard_mock) == "left_turn"
