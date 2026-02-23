import pytest
from central_manager.map import MapNode


def test_given_node_data_when_initiated_then_attributes_are_correct():
    node = MapNode("Node1", tag=10)

    assert node.id == "Node1"
    assert node.tag == 10
    assert node.left is None
    assert node.right is None
    assert node.straight is None


def test_given_nodes_when_turns_added_then_attributes_are_updated():
    node_start = MapNode("Start", 1)
    node_left = MapNode("L", 2)
    node_right = MapNode("R", 3)
    node_straight = MapNode("S", 4)

    node_start.add_left_turn(node_left)
    node_start.add_right_turn(node_right)
    node_start.add_straight_line(node_straight)

    assert node_start.left == "L"
    assert node_start.right == "R"
    assert node_start.straight == "S"


def test_given_a_node_when_to_dict_then_returns_correct_dictionary():
    node = MapNode("A", tag=1)
    node.left = "B"

    result = node.to_dict()

    assert result == {"id": "A", "tag": 1, "left": "B", "right": None, "straight": None}


def test_given_a_dictionary_when_from_dict_then_returns_correct_node_object():
    data = {"id": "X", "tag": 99, "left": "Y", "right": None, "straight": "Z"}

    node = MapNode.from_dict(data)

    assert node.id == "X"
    assert node.tag == 99
    assert node.left == "Y"
    assert node.straight == "Z"


if __name__ == "__main__":
    pytest.main()
