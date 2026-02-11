import pytest
from navigation.goal_selector import GoalMode, GoalSelector
from navigation.route_selector import RouteSelector

TEST_GRAPH = {
    "A1": {"g": "ZC1", "l": "A4", "d": "ZD1"},
    "A2": {"g": "A4", "l": "ZD1", "d": "A2"},
    "A3": {"g": "ZD1", "l": "A2", "d": "ZC1"},
    "A4": {"g": "A2", "l": "ZC1", "d": "A4"},
    "ZC1": {"l": "A1"},
    "ZC2": {"l": "A2"},
    "ZD1": {"l": "A3"},
    "ZD2": {"l": "A4"},
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


def test_given_load_goals_when_select_goal_with_go_load_then_returns_load_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZC1", "ZC2"], mode=GoalMode.GO_LOAD)

    # Assert
    assert result in ["ZC1", "ZC2"]


def test_given_drop_goals_when_select_goal_with_go_drop_then_returns_drop_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZD1", "ZD2"], mode=GoalMode.GO_DROP)

    # Assert
    assert result in ["ZD1", "ZD2"]


def test_given_mixed_goals_when_select_goal_with_go_load_then_returns_only_load_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZC1", "ZD1"], mode=GoalMode.GO_LOAD)

    # Assert
    assert result == "ZC1"


def test_given_mixed_goals_when_select_goal_with_go_drop_then_returns_only_drop_goal(
    goal_selector,
):
    # Act
    result = goal_selector.select_goal("A1", ["ZC1", "ZD1"], mode=GoalMode.GO_DROP)

    # Assert
    assert result == "ZD1"


def test_given_invalid_start_when_select_goal_then_raises_value_error(goal_selector):
    # Act, Assert
    with pytest.raises(ValueError, match="Unknown start node"):
        goal_selector.select_goal("INVALID", ["ZC1"], mode=GoalMode.GO_LOAD)
