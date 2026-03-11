import pytest
from navigation.route_selector import RouteSelector

# Map format: left, straight, right (RouteSelector accepts Map dict directly)
TEST_GRAPH = {
    "A1": {"left": "ZC1", "straight": "A4", "right": "ZD1"},
    "A2": {"left": "A4", "straight": "ZD1", "right": "A2"},
    "A3": {"left": "ZD1", "straight": "A2", "right": "ZC1"},
    "A4": {"left": "A2", "straight": "ZC1", "right": "A4"},
    "ZC1": {"straight": "A1"},
    "ZD1": {"straight": "A3"},
}


@pytest.fixture
def selector():
    return RouteSelector(graph=TEST_GRAPH)


def test_given_start_equals_goal_when_compute_path_then_returns_single_node_list(
    selector,
):
    # Act
    nodes, _ = selector.compute_path("A1", "A1")

    # Assert
    assert nodes == ["A1"]


def test_given_start_equals_goal_when_compute_path_then_returns_empty_directions(
    selector,
):
    # Act
    _, directions = selector.compute_path("A1", "A1")

    # Assert
    assert directions == []


def test_given_unknown_start_when_compute_path_then_raises_value_error(selector):
    # Act & Assert
    with pytest.raises(ValueError, match="Unknown start node"):
        selector.compute_path("INVALID", "A1")


def test_given_unknown_goal_when_compute_path_then_raises_value_error(selector):
    # Act & Assert
    with pytest.raises(ValueError, match="Unknown goal node"):
        selector.compute_path("A1", "INVALID")


def test_given_valid_start_and_goal_when_compute_path_then_returns_expected_nodes(
    selector,
):
    # Arrange
    expected_nodes = ["ZC1", "A1", "ZD1"]

    # Act
    nodes, _ = selector.compute_path("ZC1", "ZD1")

    # Assert
    assert nodes == expected_nodes


def test_given_valid_start_and_goal_when_compute_path_then_returns_expected_directions(
    selector,
):
    # Arrange: ZC1 --straight--> A1 --right--> ZD1
    expected_directions = ["straight", "right"]

    # Act
    _, directions = selector.compute_path("ZC1", "ZD1")

    # Assert
    assert directions == expected_directions
