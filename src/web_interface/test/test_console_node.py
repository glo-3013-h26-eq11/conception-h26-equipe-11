import pytest
import rclpy
from std_msgs.msg import String
from rcl_interfaces.msg import Log
from web_interface.console_node import ConsoleNode


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def console_node():
    node = ConsoleNode()
    yield node
    node.destroy_node()


@pytest.fixture
def small_console_node():
    node = ConsoleNode(message_stack_size=2)
    yield node
    node.destroy_node()


@pytest.fixture
def filter_console_node():
    node = ConsoleNode(filters=["to_filter"])
    yield node
    node.destroy_node()


def test_when_receives_log_then_publish_to_console(console_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    console_node.create_subscription(String, "/console", capture_callback, 10)

    input_log = Log()
    input_log.file = "test_file"

    console_node.log_callback(input_log)

    rclpy.spin_once(console_node, timeout_sec=0.1)

    assert len(received_msgs) == 1
    assert "test_file" in received_msgs[0]


def test_when_receives_log_overflow_then_erase_old_logs(small_console_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    small_console_node.create_subscription(String, "/console", capture_callback, 10)

    input_log_1 = Log()
    input_log_1.file = "test_1"

    input_log_2 = Log()
    input_log_2.file = "test_2"

    input_log_3 = Log()
    input_log_3.file = "test_3"

    small_console_node.log_callback(input_log_1)
    small_console_node.log_callback(input_log_2)
    small_console_node.log_callback(input_log_3)

    for i in range(3):
        rclpy.spin_once(small_console_node, timeout_sec=0.1)

    assert len(received_msgs) == 3
    assert "test_2" in received_msgs[-1]
    assert "test_3" in received_msgs[-1]
    assert "test_1" not in received_msgs[-1]


def test_when_receives_log_to_filter_then_nothing_is_published(filter_console_node):
    received_msgs = []

    def capture_callback(msg):
        received_msgs.append(msg.data)

    filter_console_node.create_subscription(String, "/console", capture_callback, 10)

    input_log_1 = Log()
    input_log_1.file = "to_filter"

    filter_console_node.log_callback(input_log_1)

    rclpy.spin_once(filter_console_node, timeout_sec=0.1)

    assert len(received_msgs) == 0
