import pytest
from unittest.mock import patch

from central_manager.states.to_load.at_intersection_to_load_state import (
    AtIntersectionToLoadState,
)
from central_manager.states.node_action_enum import NodeAction
from unittest.mock import MagicMock


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


@patch("rclpy.spin_until_future_complete", return_value=None)
def test_left_turn_transition(blackboard_mock):
    fake_node = MagicMock()

    fake_client = MagicMock()
    fake_client.wait_for_service.return_value = True
    fake_client.call_async.return_value = FakeFuture(NodeAction.LEFT_TURN.value)

    fake_node.create_client.return_value = fake_client

    state = AtIntersectionToLoadState(fake_node)

    blackboard = {"node": fake_node}

    outcome = state.execute(blackboard)

    assert outcome == "left_turn"
