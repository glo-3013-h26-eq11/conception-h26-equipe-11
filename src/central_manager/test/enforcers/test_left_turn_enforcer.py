import json
import time
import pytest
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from unittest.mock import Mock


@pytest.fixture
def enforcer():
    mock_pub = Mock()
    return LeftTurnEnforcer(mock_pub)


def test_given_turn_finished_when_enforce_cmd_then_return_empty_twist(enforcer):
    enforcer.turn_finished = True
    initial_command = Twist()
    initial_command.linear.x = 5.0
    initial_command.angular.z = 5.0

    resulting_command = enforcer.enforce_cmd(initial_command)

    assert resulting_command.linear.x == 0
    assert resulting_command.angular.z == 0


def test_when_imu_reaches_90_degrees_then_publish_turn_over(enforcer, monkeypatch):
    enforcer.last_imu_time = 1.0
    monkeypatch.setattr(time, "monotonic", lambda: 3.5)

    msg = String()
    msg.data = json.dumps({"gyro_z": 40.0})

    enforcer.imu_callback(msg)

    enforcer.turn_over_publisher.publish.assert_called_once()
    assert enforcer.turn_finished is True


def test_given_not_finished_when_enforce_cmd_then_turn(enforcer):
    initial_command = Twist()

    resulting_command = enforcer.enforce_cmd(initial_command)

    assert resulting_command.linear.x != 0
    assert resulting_command.angular.z != 0


def test_when_update_real_speed_does_nothing_on_left_turn_enforcer(enforcer):
    real_speed_command = Twist()
    real_speed_command.linear.x = 0.4

    # update_with_real_speed is IMU-driven for left turn; no distance book-keeping
    enforcer.update_with_real_speed(real_speed_command)

    assert enforcer.travel_distance_already_done == 0
