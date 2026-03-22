from central_manager.enforcer_manager_node import EnforcerManagerNode
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool, Float32MultiArray
import pytest
import rclpy


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    if not rclpy.ok():
        rclpy.init()
    yield
    if rclpy.ok():
        rclpy.shutdown()


@pytest.fixture
def node():
    enforcer_manager_node = EnforcerManagerNode()
    yield enforcer_manager_node
    enforcer_manager_node.destroy_node()


def test_given_load_not_detected_when_load_callback_with_true_then_updates_to_load_detected(
    node,
):
    # Arrange
    node.merchandise_enforcer.load_detected = False

    # Act
    load_msg = Bool()
    load_msg.data = True
    node.load_callback(load_msg)

    # Assert
    assert node.merchandise_enforcer.load_detected is True


def test_given_load_detected_when_load_callback_with_false_then_updates_to_load_not_detected(
    node,
):
    # Arrange
    node.merchandise_enforcer.load_detected = True

    # Act
    load_msg = Bool()
    load_msg.data = False
    node.load_callback(load_msg)

    # Assert
    assert node.merchandise_enforcer.load_detected is not True


def test_given_destination_zc_when_load_callback_with_true_then_publishes_invalid_destination(
    node,
):
    # Arrange
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Bool, "/merchandise_destination_invalid", call_back, 10)

    node.merchandise_enforcer.destination = "ZC1"
    load_msg = Bool()
    load_msg.data = True

    # Act
    node.load_callback(load_msg)
    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert len(received_msgs) == 1

    invalid_dest_msg = received_msgs[0].data
    assert invalid_dest_msg is True


def test_given_destination_zd_when_load_callback_with_true_then_publishes_nothing(node):
    # Arrange
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Bool, "/merchandise_destination_invalid", call_back, 10)

    node.merchandise_enforcer.destination = "ZD2"
    load_msg = Bool()
    load_msg.data = True

    # Act
    node.load_callback(load_msg)
    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert received_msgs == []


def test_given_any_destination_when_load_callback_with_false_then_publishes_nothing(
    node,
):
    # Arrange
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Bool, "/merchandise_destination_invalid", call_back, 10)

    node.merchandise_enforcer.destination = "ZC1"
    load_msg = Bool()
    load_msg.data = False

    # Act
    node.load_callback(load_msg)
    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert received_msgs == []


def test_given_load_detected_and_destination_zc_when_cmd_callback_then_blockes_and_publishes_safe(
    node,
):
    # Arrange
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Twist, "/cmd_vel_safe", call_back, 10)

    node.merchandise_enforcer.destination = "ZC1"
    node.merchandise_enforcer.load_detected = True

    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2

    # Act
    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert len(received_msgs) == 1

    cmd_vel_safe = received_msgs[0]
    assert cmd_vel_safe.linear.x == 0.0
    assert cmd_vel_safe.angular.z == 0.0


def test_given_load_detected_and_destination_zd_when_cmd_callback_the_allows_and_publishes_safe(
    node,
):
    # Arrange
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Twist, "/cmd_vel_safe", call_back, 10)

    node.merchandise_enforcer.destination = "ZD2"
    node.merchandise_enforcer.load_detected = True

    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2

    # Act
    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert len(received_msgs) == 1

    cmd_vel_safe = received_msgs[0]
    assert cmd_vel_safe.linear.x == 0.5
    assert cmd_vel_safe.angular.z == 0.2


def test_given_load_not_detected_and_destination_when_cmd_callback_then_allows_and_publishes_safe(
    node,
):
    # Arrange
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Twist, "/cmd_vel_safe", call_back, 10)

    node.merchandise_enforcer.destination = "ZD2"
    node.merchandise_enforcer.load_detected = False

    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2

    # Act
    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert len(received_msgs) == 1

    cmd_vel_safe = received_msgs[0]
    assert cmd_vel_safe.linear.x == 0.5
    assert cmd_vel_safe.angular.z == 0.2


def test_given_destination_when_route_nodes_callback_then_updates_destination(node):
    # Arrange
    node.merchandise_enforcer.destination = "ZC1"

    # Act
    test_nodes = ["ZC1", "A1", "A4", "ZD1"]
    msg = String()
    msg.data = json.dumps(test_nodes)
    node.route_nodes_callback(msg)

    # Assert
    assert node.merchandise_enforcer.destination == "ZD1"


def test_given_aruco_5x5_detection_when_callback_then_sets_stop_and_publishes_zero_cmd(
    node,
):
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Twist, "/cmd_vel_safe", call_back, 10)

    msg = Float32MultiArray()
    msg.data = [1.0, 0.75]

    node.aruco_5x5_callback(msg)
    rclpy.spin_once(node, timeout_sec=0.1)

    assert node.stop_sign_enforcer.stop_detected is True
    assert len(received_msgs) == 1
    assert received_msgs[0].linear.x == 0.0
    assert received_msgs[0].angular.z == 0.0


def test_given_stop_detected_when_cmd_callback_then_publishes_stopped_cmd(node):
    received_msgs = []

    def call_back(msg):
        received_msgs.append(msg)

    node.create_subscription(Twist, "/cmd_vel_safe", call_back, 10)
    node.stop_sign_enforcer.stop_detected = True
    node.stop_sign_enforcer.stop_duration = 10.0

    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2

    node.cmd_callback(cmd)
    rclpy.spin_once(node, timeout_sec=0.1)

    assert len(received_msgs) == 1
    assert received_msgs[0].linear.x == 0.0
    assert received_msgs[0].angular.z == 0.0
