import pytest
import json
from map_manager.model import Map, MapNode


@pytest.fixture
def sample_nodes():
    node_a = MapNode("A", tag=1)
    node_b = MapNode("B", tag=2)
    node_a.add_straight_line(node_b)
    return [node_a, node_b]


@pytest.fixture
def basic_map(sample_nodes):
    return Map(sample_nodes)


def test_given_duplicate_nodes_when_initiated_then_value_error_is_raised():
    node_a1 = MapNode("A")
    node_a2 = MapNode("A")

    with pytest.raises(ValueError, match="Duplicate node ID detected"):
        Map([node_a1, node_a2])


def test_given_a_invalid_node_id_when_get_map_node_then_value_error_is_raised():
    node_a = MapNode("A")
    my_map = Map([node_a])

    with pytest.raises(ValueError, match="not found in map"):
        my_map.get_map_node("Z")


def test_given_a_map_when_to_dict_then_returns_correct_dictionary(basic_map):
    result = basic_map.to_dict()

    assert result["A"]["id"] == "A"
    assert result["A"]["straight"] == "B"
    assert result["B"]["id"] == "B"


def test_given_a_map_when_to_json_then_returns_correct_json_string(basic_map):
    json_str = basic_map.to_json()
    data = json.loads(json_str)

    assert "A" in data
    assert data["A"]["straight"] == "B"


def test_given_a_json_string_when_from_json_then_returns_correct_map_object():
    json_data = (
        '{"A": {"id": "A", "tag": 1, "straight": "B", "left": null, "right": null}, '
        '"B": {"id": "B", "tag": 2, "straight": null, "left": null, "right": null}}'
    )
    new_map = Map.from_json(json_data)

    assert len(new_map.map_nodes) == 2
    assert new_map.get_map_node("A").straight == "B"
    assert new_map.get_map_node("A").tag == 1


if __name__ == "__main__":
    pytest.main()
