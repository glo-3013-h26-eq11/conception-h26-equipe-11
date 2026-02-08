import pytest
import rclpy
from std_msgs.msg import String
import json
from navigation.rover_interface import RoverInterfaceSubscriber, ROVER_COMMAND


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def rover_node():
    node = RoverInterfaceSubscriber()
    yield node
    node.destroy_node()


def test_when_receives_valid_command_then_publishes_json(rover_node):
    # Arrange
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    rover_node.create_subscription(String, "rover_port", capture_callback, 10)

    input_msg = String()
    input_msg.data = "FORWARD"

    # Act
    rover_node.listener_command_callback(input_msg)

    rclpy.spin_once(rover_node, timeout_sec=0.1)

    # Assert
    expected_result = ROVER_COMMAND[input_msg.data]

    assert len(received_msgs) == 1
    assert received_msgs[0] == json.dumps(expected_result)


def test_when_receives_invalid_command_then_raises_error(rover_node):
    # Arrange
    bad_msg = String()

    bad_msg.data = "GARBAGE COMMAND"
    # Act, Assert
    with pytest.raises(ValueError):
        rover_node.listener_command_callback(bad_msg)
