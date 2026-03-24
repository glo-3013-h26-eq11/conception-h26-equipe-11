import pytest
from navigation.goal_selector import GoalMode, GoalSelector
from navigation.route_selector import RouteSelector

TEST_GRAPH = {
    "A1": {"left": "ZC1", "straight": "A4", "right": "ZD1"},
    "A2": {"left": "A4", "straight": "ZD1", "right": "A2"},
    "A3": {"left": "ZD1", "straight": "A2", "right": "ZC1"},
    "A4": {"left": "A2", "straight": "ZC1", "right": "A4"},
    "ZC1": {"straight": "A1"},
    "ZC2": {"straight": "A2"},
    "ZD1": {"straight": "A3"},
    "ZD2": {"straight": "A4"},
}


@pytest.fixture
def goal_selector():
    route_selector = RouteSelector(graph=TEST_GRAPH)
    return GoalSelector(route_selector)


def test_given_no_goals_when_select_goal_then_returns_none(goal_selector):
    # Act
    result = goal_selector.select_goal("A1", [])

    # Assert
    assert result is None


def test_given_invalid_mode_when_select_goal_then_raises_value_error(goal_selector):
    # Act, Assert
    with pytest.raises(ValueError, match="INVALID"):
        goal_selector.select_goal("A1", ["ZC1"], mode="INVALID")


def test_given_load_goals_when_select_goal_with_go_load_then_returns_closest_load_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZC1", "ZC2"], mode=GoalMode.GO_LOAD)

    # Assert
    assert result == "ZC1"


def test_given_drop_goals_when_select_goal_with_GO_DEPOSIT_then_returns_closest_drop_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZD1", "ZD2"], mode=GoalMode.GO_DEPOSIT)

    # Assert
    assert result == "ZD1"


def test_given_mixed_goals_when_select_goal_with_go_load_then_returns_only_load_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZC1", "ZD1"], mode=GoalMode.GO_LOAD)

    # Assert
    assert result == "ZC1"


def test_given_mixed_goals_when_select_goal_with_GO_DEPOSIT_then_returns_only_drop_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZC1", "ZD1"], mode=GoalMode.GO_DEPOSIT)

    # Assert
    assert result == "ZD1"


def test_given_invalid_start_when_select_goal_then_raises_value_error(goal_selector):
    # Act, Assert
    with pytest.raises(ValueError, match="Unknown start node"):
        goal_selector.select_goal("INVALID", ["ZC1"], mode=GoalMode.GO_LOAD)
