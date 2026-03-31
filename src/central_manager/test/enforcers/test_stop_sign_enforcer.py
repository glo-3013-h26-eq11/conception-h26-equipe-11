import time
import pytest
from geometry_msgs.msg import Twist
from central_manager.enforcers.stop_sign_enforcer import (
    StopSignEnforcer,
    _State,
    STOP_DURATION,
    BRAKE_START_DIST,
)
from unittest.mock import Mock


@pytest.fixture
def enforcer():
    stop_over_publisher = Mock()
    return StopSignEnforcer(stop_over_publisher)


def make_cmd(v=1.0, w=0.0):
    cmd = Twist()
    cmd.linear.x = v
    cmd.angular.z = w
    return cmd


def test_given_no_specification_when_checked_then_state_is_idle(enforcer):
    assert enforcer._state == _State.IDLE


def test_given_enforcer_close_to_stop_when_enforce_then_state_is_braking(enforcer):
    cmd = make_cmd()

    enforcer.update_distance(BRAKE_START_DIST)
    enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.BRAKING


def test_given_enforcer_braking_when_approaching_stop_then_speed_reduces(enforcer):
    cmd = make_cmd(1.0)

    enforcer.update_distance(BRAKE_START_DIST)
    enforcer.enforce_cmd(cmd)
    enforcer.update_distance(BRAKE_START_DIST - 0.1)
    out = enforcer.enforce_cmd(cmd)

    assert out.linear.x < cmd.linear.x
    assert out.linear.x >= 0.2


def test_given_enforcer_braking_and_close_to_stop_when_enforce_then_state_is_stopped(
    enforcer,
):
    cmd = make_cmd(1.0)

    enforcer.update_distance(BRAKE_START_DIST)
    enforcer.enforce_cmd(cmd)
    enforcer.update_distance(BRAKE_START_DIST - 0.3)
    out = enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.STOPPED
    assert out.linear.x == 0.0


def test_given_enforcer_stopped_when_wait_time_done_then_publish_stop_over(enforcer):
    enforcer._state = _State.STOPPED
    enforcer._stop_start = time.time() - STOP_DURATION - 0.1
    cmd = make_cmd(1.0)

    enforcer.update_distance(0.6)
    enforcer.enforce_cmd(cmd)

    enforcer.stop_over_publisher.publish.assert_called_once()
