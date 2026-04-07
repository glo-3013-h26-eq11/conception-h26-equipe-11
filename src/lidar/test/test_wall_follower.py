import math
import pytest
import rclpy
from sensor_msgs.msg import LaserScan
from lidar.wall_follower import (
    WallFollowNode,
    angle_to_distance,
    is_valid_lidar_scan,
    SPEED,
    WHEELBASE,
    AFTER_CORNER_THRESHOLD,
    THETA_DEG,
    MAX_STEERING,
    RIGHT_CORNER_SPEED,
)


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture
def wall_follow_node():
    node = WallFollowNode()
    yield node
    node.destroy_node()


def create_scan(num_points=360, default_distance=5.0):
    scan = LaserScan()
    scan.ranges = [default_distance] * num_points
    scan.angle_min = -math.pi
    scan.angle_increment = 2 * math.pi / num_points
    return scan


def test_when_angle_in_range_then_returns_expected_distance():
    # Arrange
    lidar_array = [1.0, 2.0, 3.0, 4.0, 5.0]
    angle_min = -1.0
    angle_increment = 0.5

    # Act
    result = angle_to_distance(0.0, lidar_array, angle_min, angle_increment)

    # Assert
    assert result == 3.0


def test_when_angle_too_small_then_clamps_to_first_value():
    # Arrange
    lidar_array = [1.0, 2.0, 3.0]
    angle_min = 0.0
    angle_increment = 0.1

    # Act
    result = angle_to_distance(-10.0, lidar_array, angle_min, angle_increment)

    # Assert
    assert result == 1.0


def test_when_angle_too_large_then_clamps_to_last_value():
    # Arrange
    lidar_array = [1.0, 2.0, 3.0]
    angle_min = 0.0
    angle_increment = 0.1

    # Act
    result = angle_to_distance(10.0, lidar_array, angle_min, angle_increment)

    # Assert
    assert result == 3.0


def test_when_scan_value_is_valid_then_returns_true():
    # Arrange / Act / Assert
    assert is_valid_lidar_scan(1.5) is True
    assert is_valid_lidar_scan(0.1) is True
    assert is_valid_lidar_scan(10.0) is True


def test_when_scan_value_is_invalid_then_returns_false():
    # Arrange / Act / Assert
    assert is_valid_lidar_scan(float("inf")) is False
    assert is_valid_lidar_scan(float("-inf")) is False
    assert is_valid_lidar_scan(float("nan")) is False
    assert is_valid_lidar_scan(0.0) is False
    assert is_valid_lidar_scan(-1.0) is False


def test_when_node_is_created_then_initial_state_is_correct(wall_follow_node):
    # Assert
    assert wall_follow_node.get_name() == "wall_follow_node"
    assert wall_follow_node.last_time is None
    assert wall_follow_node.last_steering == 0.0
    assert len(wall_follow_node.last_errors_window) == 0


def test_when_positive_steering_then_publishes_positive_velocity(wall_follow_node):
    # Arrange
    published_msgs = []

    def fake_publish(msg):
        published_msgs.append(msg)

    wall_follow_node.drive_pub.publish = fake_publish

    steering = 0.5
    expected_angular_z = SPEED * math.tan(steering) / WHEELBASE

    # Act
    wall_follow_node.send_control_command(SPEED, steering)

    # Assert
    assert len(published_msgs) == 1
    assert published_msgs[0].linear.x == pytest.approx(SPEED)
    assert published_msgs[0].angular.z == pytest.approx(expected_angular_z)
    assert published_msgs[0].angular.z > 0


def test_when_negative_steering_then_publishes_negative_velocity(wall_follow_node):
    # Arrange
    published_msgs = []

    def fake_publish(msg):
        published_msgs.append(msg)

    wall_follow_node.drive_pub.publish = fake_publish

    steering = -0.5
    expected_angular_z = SPEED * math.tan(steering) / WHEELBASE

    # Act
    wall_follow_node.send_control_command(SPEED, steering)

    # Assert
    assert len(published_msgs) == 1
    assert published_msgs[0].linear.x == pytest.approx(SPEED)
    assert published_msgs[0].angular.z == pytest.approx(expected_angular_z)
    assert published_msgs[0].angular.z < 0


def test_when_invalid_wall_measurements_then_repeats_last_command(
    wall_follow_node, monkeypatch
):
    # Arrange
    commands = []

    def fake_send_control_command(speed, steering):
        commands.append((speed, steering))

    monkeypatch.setattr(
        wall_follow_node, "send_control_command", fake_send_control_command
    )

    wall_follow_node.last_steering = 0.3

    scan = create_scan(default_distance=float("inf"))

    # Act
    wall_follow_node.lidar_callback(scan)

    # Assert
    assert len(commands) == 1
    assert commands[0][0] == pytest.approx(SPEED)
    assert commands[0][1] == pytest.approx(0.3)


def test_when_big_b_then_steering_right_max(wall_follow_node):
    b = AFTER_CORNER_THRESHOLD + 0.1
    a = 0.5

    initial_speed = RIGHT_CORNER_SPEED
    initial_steering = 0.0
    theta_rad = math.radians(THETA_DEG)

    scan = create_scan(default_distance=float("inf"))

    result_speed, result_steering = wall_follow_node.filter_intersections(
        a, b, theta_rad, initial_speed, initial_steering, scan
    )

    assert result_speed == initial_speed
    assert result_steering == -MAX_STEERING
