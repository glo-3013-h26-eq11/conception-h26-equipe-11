import pytest
from navigation.route_selector import RouteSelector

TEST_GRAPH = {
    "A1": {"g": "ZC1", "l": "A4", "d": "ZD1"},
    "A2": {"g": "A4", "l": "ZD1", "d": "A2"},
    "A3": {"g": "ZD1", "l": "A2", "d": "ZC1"},
    "A4": {"g": "A2", "l": "ZC1", "d": "A4"},
    "ZC1": {"l": "A1"},
    "ZD1": {"l": "A3"},
}

@pytest.fixture
def selector():
    return RouteSelector(graph=TEST_GRAPH)

def test_compute_route_returns_empty_list_when_start_equals_goal(selector):
    route = selector.compute_route("A1", "A1")

    assert route == []

def test_compute_route_returns_none_when_start_is_unknown(selector):
    route = selector.compute_route("INVALID", "A1")

    assert route is None

def test_compute_route_returns_none_when_goal_is_unknown(selector):
    route = selector.compute_route("A1", "INVALID")

    assert route is None

def test_compute_route_returns_list_when_route_exists(selector):
    route = selector.compute_route("A1", "ZC1")

    assert isinstance(route, list)

def test_compute_route_returns_correct_path(selector):
    route = selector.compute_route("ZC1", "ZD1")

    assert route is not None
    current = "ZC1"
    for direction in route:
        assert direction in selector.graph[current]
        current = selector.graph[current][direction]
    assert current == "ZD1"
