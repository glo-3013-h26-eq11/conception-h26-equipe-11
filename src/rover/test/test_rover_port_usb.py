import pytest
import rclpy
from std_msgs.msg import String
from rover.rover_port_usb import RoverPortSubscriber
import os
import pty
import serial
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def rover_usb_node():
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)
    serial_port = serial.Serial(slave_name, 115200)

    node = RoverPortSubscriber(serial_port=serial_port)

    yield node, master

    node.destroy_node()


def test_given_json_then_publishes_to_port(rover_usb_node):
    # Arrange
    rover_node, master = rover_usb_node

    expected_data = '{"T": 1, "L": 0.1, "R": 0.1}'

    input_msg = String()
    input_msg.data = expected_data

    # Act
    rover_node.listener_json_callback(input_msg)

    # Assert
    data = os.read(master, 1024)
    data_string = data.decode()
    assert expected_data in data_string
