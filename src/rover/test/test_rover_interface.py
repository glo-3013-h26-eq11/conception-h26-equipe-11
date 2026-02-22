import pytest
import rclpy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from rover.rover_interface import RoverInterfaceSubscriber
import json


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

    input_msg = Twist()
    input_msg.linear.x = 2.0
    input_msg.angular.z = 2.0

    # Act
    rover_node.listener_command_callback(input_msg)

    rclpy.spin_once(rover_node, timeout_sec=0.1)

    # Assert
    expected = rover_node.create_movement_dictionnary(2.0, 2.0)

    assert len(received_msgs) == 1
    assert received_msgs[0] == json.dumps(expected)
