import time
import pytest
from geometry_msgs.msg import Twist
from central_manager.stopSignEnforcer import StopSignEnforcer, _State


@pytest.fixture
def enforcer():
    return StopSignEnforcer()


def make_cmd(v=1.0, w=0.0):
    cmd = Twist()
    cmd.linear.x = v
    cmd.angular.z = w
    return cmd


def test_given_no_specification_when_checked_then_state_is_idle(enforcer):
    assert enforcer._state == _State.IDLE


def test_given_enforcer_close_to_stop_when_enforce_then_state_is_braking(enforcer):
    cmd = make_cmd()

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.BRAKING


def test_given_enforcer_braking_when_approaching_stop_then_speed_reduces(enforcer):
    cmd = make_cmd(1.0)

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)
    enforcer.update_distance(0.8)
    out = enforcer.enforce_cmd(cmd)

    assert out.linear.x < cmd.linear.x
    assert out.linear.x >= 0.3


def test_given_enforcer_braking_and_close_to_stop_when_enforce_then_state_is_stopped(
    enforcer,
):
    cmd = make_cmd(1.0)

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)
    enforcer.update_distance(0.6)
    out = enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.STOPPED
    assert out.linear.x == 0.0


def test_given_enforcer_stopped_when_stop_duration_elapsed_then_state_is_cooldown(
    enforcer,
):
    enforcer.stop_duration = 0.2
    cmd = make_cmd()

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)
    enforcer.update_distance(0.6)
    enforcer.enforce_cmd(cmd)
    time.sleep(0.25)
    out = enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.COOLDOWN
    assert out.linear.x == cmd.linear.x


def test_given_enforcer_in_cooldown_when_cooldown_elapsed_then_state_is_idle(enforcer):
    enforcer.stop_duration = 0.1
    cmd = make_cmd()

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)
    enforcer.update_distance(0.6)
    enforcer.enforce_cmd(cmd)
    time.sleep(0.15)
    enforcer.enforce_cmd(cmd)
    time.sleep(2.1)
    enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.IDLE
