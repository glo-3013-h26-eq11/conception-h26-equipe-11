import pytest
import rclpy
from unittest.mock import MagicMock, patch
from central_manager.map_processor_node import MapProcessorNode
from central_manager.model import Map, MapNode
from std_msgs.msg import String


@pytest.fixture(scope="session", autouse=True)
def ros_context():
    if not rclpy.ok():
        rclpy.init()
    yield
    if rclpy.ok():
        rclpy.shutdown()


@pytest.fixture
def map_processor_node():
    node = MapProcessorNode()
    node.publisher = MagicMock()
    node._mock_logger = MagicMock()
    with patch.object(node, "get_logger", return_value=node._mock_logger):
        yield node

    node.destroy_node()


def test_given_valid_nodes_csv_lines_when_parse_nodes_then_returns_correct_nodes_dict(
    map_processor_node,
):
    csv_lines = ["position_dans_ville,aruco_id", "A1,1", "ZC1,6"]

    nodes_dict = map_processor_node._parse_nodes(csv_lines)

    assert len(nodes_dict) == 2
    assert nodes_dict["A1"].id == "A1"
    assert nodes_dict["A1"].tag == 1
    assert nodes_dict["ZC1"].id == "ZC1"
    assert nodes_dict["ZC1"].tag == 6


def test_given_csv_with_empty_lines_when_parse_nodes_then_ignores_empty_lines(
    map_processor_node,
):
    csv_lines = ["position_dans_ville,aruco_id", "", "A1,1", "  ", "ZC1,6"]

    nodes_dict = map_processor_node._parse_nodes(csv_lines)

    assert len(nodes_dict) == 2
    assert "A1" in nodes_dict
    assert "ZC1" in nodes_dict


def test_given_valid_transitions_csv_lines_when_parse_transitions_then_nodes_are_linked(
    map_processor_node,
):
    nodes_dict = {
        "A1": MapNode("A1", 1),
        "A4": MapNode("A4", 2),
        "ZC1": MapNode("ZC1", 3),
    }
    csv_lines = ["Origine,Direction,DestinationStart", "A1,g,ZC1", "A1,l,A4"]

    map_processor_node._parse_transitions(csv_lines, nodes_dict)

    assert nodes_dict["A1"].left == "ZC1"
    assert nodes_dict["A1"].straight == "A4"
    assert nodes_dict["A1"].right is None


def test_given_transition_with_unknown_node_when_parse_transitions_then_link_is_not_added(
    map_processor_node,
):
    nodes_dict = {"A1": MapNode("A1", 1)}
    csv_lines = ["Origine,Direction,DestinationStart", "A1,g,UNKNOWN"]

    map_processor_node._parse_transitions(csv_lines, nodes_dict)

    assert nodes_dict["A1"].left is None


def test_given_full_raw_csv_data_when_parse_csv_file_then_returns_complete_map_object(
    map_processor_node,
):
    raw_data = (
        "Origine,Direction,DestinationStart\n"
        "A1,g,ZC1\n"
        "A1,l,A4\n"
        "---\n"
        "position_dans_ville,aruco_id\n"
        "A1,1\n"
        "ZC1,6\n"
        "A4,4"
    )

    result_map = map_processor_node.parse_csv_file(raw_data)

    assert isinstance(result_map, Map)
    assert len(result_map.map_nodes) == 3
    assert result_map.get_map_node("A1").left == "ZC1"
    assert result_map.get_map_node("A1").straight == "A4"


def test_given_incomplete_csv_data_when_parse_csv_file_then_raises_value_error(
    map_processor_node,
):
    raw_data = "Only one section here"

    with pytest.raises(
        ValueError, match="Input must contain two sections separated by '---'"
    ):
        map_processor_node.parse_csv_file(raw_data)


def test_given_a_raw_map_msg_when_map_callback_then_publishes_processed_json_map(
    map_processor_node,
):
    msg = String()
    msg.data = (
        "Origine,Direction,DestinationStart\n"
        "A1,l,A4\n"
        "---\n"
        "position_dans_ville,aruco_id\n"
        "A1,1\n"
        "A4,4"
    )

    map_processor_node.map_callback(msg)

    assert map_processor_node.publisher.publish.called
    published_msg = map_processor_node.publisher.publish.call_args[0][0]
    assert isinstance(published_msg, String)
    assert '"A1"' in published_msg.data
    assert '"A4"' in published_msg.data


def test_given_invalid_msg_data_when_map_callback_then_logs_error(map_processor_node):
    msg = String()
    msg.data = "invalid data without separator"

    with patch.object(
        map_processor_node, "get_logger", return_value=map_processor_node._mock_logger
    ):
        map_processor_node.map_callback(msg)

    map_processor_node._mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main()
