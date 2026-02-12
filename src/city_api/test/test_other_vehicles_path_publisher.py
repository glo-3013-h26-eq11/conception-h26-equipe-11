import pytest
from unittest.mock import MagicMock
import rclpy
from city_api.other_vehicles_path_publisher import OtherVehiclesPathPublisher
from std_msgs.msg import String
import json


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture()
def other_vehicles_path_node():
    city_interface = MagicMock()

    city_interface.get_vehicles.return_value = {"test": 1}

    other_vehicles_path_node = OtherVehiclesPathPublisher(city_interface)

    yield other_vehicles_path_node

    other_vehicles_path_node.destroy_node()


def test_when_receives_valid_command_then_publishes_json(
    other_vehicles_path_node,
):
    # Arrange
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    other_vehicles_path_node.create_subscription(
        String, "/city_api/other_vehicles_path", capture_callback, 10
    )

    # Act
    other_vehicles_path_node.fetch()

    rclpy.spin_once(other_vehicles_path_node, timeout_sec=0.1)

    # Assert
    expected_result = {"test": 1}

    assert len(received_msgs) == 1
    assert received_msgs[0] == json.dumps(expected_result)
