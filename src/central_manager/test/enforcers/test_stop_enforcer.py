import pytest
from central_manager.enforcers.stop_enforcer import StopEnforcer
from geometry_msgs.msg import Twist
import time
from central_manager.enforcers.stop_enforcer import (
    STOP_DURATION,
)


@pytest.fixture
def enforcer():
    return StopEnforcer()


def test_given_stop_enforcer_just_started_when_enforce_then_twist_is_zero(enforcer):
    cmd_input = Twist()
    cmd_input.linear.x = 5.0
    cmd_input.angular.z = 5.0

    cmd_result = enforcer.enforce_cmd(cmd_input)

    assert cmd_result == Twist()


def test_given_full_stop_when_enforce_then_twist_is_not_changed(enforcer):
    cmd_input = Twist()
    cmd_input.linear.x = 5.0
    cmd_input.angular.z = 5.0

    increments = int(STOP_DURATION / 0.1 + 1)
    for _ in range(increments):
        enforcer.update_with_real_speed(cmd_input)
        time.sleep(0.1)
    cmd_result = enforcer.enforce_cmd(cmd_input)

    assert cmd_result == cmd_input
