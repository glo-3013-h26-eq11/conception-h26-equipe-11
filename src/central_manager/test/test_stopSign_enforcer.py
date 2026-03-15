import time
import pytest
from geometry_msgs.msg import Twist
from central_manager.stopSignEnforcer import StopSignEnforcer

@pytest.fixture
def enforcer():
    return StopSignEnforcer()

def make_cmd(v=1.0, w=0.0):
    cmd = Twist()
    cmd.linear.x = v
    cmd.angular.z = w
    return cmd


def test_initial_state():
    enforcer = StopSignEnforcer()
    assert enforcer._state == _State.IDLE


def test_detect_stop_and_enter_braking():
    enforcer = StopSignEnforcer()
    cmd = make_cmd()

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.BRAKING


def test_braking_reduces_speed():
    enforcer = StopSignEnforcer()
    cmd = make_cmd(1.0)

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)

    enforcer.update_distance(0.8)
    out = enforcer.enforce_cmd(cmd)

    assert out.linear.x < cmd.linear.x
    assert out.linear.x >= 0.3


def test_stop_state():
    enforcer = StopSignEnforcer()
    cmd = make_cmd(1.0)

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)

    enforcer.update_distance(0.6)
    out = enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.STOPPED
    assert out.linear.x == 0.0


def test_resume_after_stop_duration():
    enforcer = StopSignEnforcer(stop_duration=0.2)
    cmd = make_cmd()

    enforcer.update_distance(0.9)
    enforcer.enforce_cmd(cmd)

    enforcer.update_distance(0.6)
    enforcer.enforce_cmd(cmd)

    time.sleep(0.25)

    out = enforcer.enforce_cmd(cmd)

    assert enforcer._state == _State.COOLDOWN
    assert out.linear.x == cmd.linear.x


def test_cooldown_returns_to_idle():
    enforcer = StopSignEnforcer(stop_duration=0.1)
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