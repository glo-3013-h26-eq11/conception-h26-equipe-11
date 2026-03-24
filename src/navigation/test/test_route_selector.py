import pytest
from navigation.route_selector import RouteSelector

TEST_GRAPH = {
    "A1": {"id": "A1", "tag": 1, "right": "ZD1", "left": "ZC1", "straight": "A4"},
    "A2": {"id": "A2", "tag": 2, "right": "A2", "left": "A4", "straight": "ZD1"},
    "A3": {"id": "A3", "tag": 3, "right": "ZC1", "left": "ZD1", "straight": "A2"},
    "A4": {"id": "A4", "tag": 4, "right": "A4", "left": "A2", "straight": "ZC1"},
    "ZD1": {"id": "ZD1", "tag": 5, "right": None, "left": None, "straight": "A3"},
    "ZC1": {"id": "ZC1", "tag": 6, "right": None, "left": None, "straight": "A1"},
}

INT = 1


@pytest.fixture
def selector():
    return RouteSelector(graph=TEST_GRAPH)


@pytest.fixture
def selector_no_graph():
    return RouteSelector(graph=None)


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


def test_given_graph_when_tag_to_id_then_return_corresponding_id(selector):
    id = selector.tag_to_id(tag=INT)

    assert id == "A1"


def test_given_no_graph_when_tag_to_id_then_assert_value_error(selector_no_graph):
    with pytest.raises(ValueError):
        selector_no_graph.tag_to_id(1)
