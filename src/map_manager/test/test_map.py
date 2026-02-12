import pytest
from map_manager.model import Map, MapNode

@pytest.fixture
def sample_nodes():
    node_a = MapNode("A")
    node_b = MapNode("B")
    node_c = MapNode("C")
    node_d = MapNode("D")
    
    return [node_a, node_b, node_c, node_d]

@pytest.fixture
def basic_map(sample_nodes):
    return Map(sample_nodes)


def test_given_no_nodes_when_initiated_then_value_error_is_raised():
    with pytest.raises(ValueError, match="Node list cannot be empty"):
        Map([])


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


if __name__ == "__main__":
    pytest.main()