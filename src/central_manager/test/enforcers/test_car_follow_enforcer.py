import time
import pytest
from geometry_msgs.msg import Twist
from central_manager.enforcers.car_follow_enforcer import (
    CarFollowEnforcer,
    VEHICLE_STALE_SEC,
)
from navigation.current_node_from_aruco_node import SAFE_DISTANCE_TO_CAR


@pytest.fixture
def enforcer():
    return CarFollowEnforcer()


def _cmd(linear_x=0.5, angular_z=0.0):
    cmd = Twist()
    cmd.linear.x = linear_x
    cmd.angular.z = angular_z
    return cmd


def test_no_detection_passes_cmd_unchanged(enforcer):
    cmd = _cmd(0.5)
    result = enforcer.enforce_cmd(cmd)
    assert result.linear.x == pytest.approx(0.5)


def test_far_distance_full_speed(enforcer):
    enforcer.update_distance(SAFE_DISTANCE_TO_CAR * 2)
    result = enforcer.enforce_cmd(_cmd(0.5))
    assert result.linear.x == pytest.approx(0.5)


def test_at_safe_distance_stops(enforcer):
    enforcer.update_distance(SAFE_DISTANCE_TO_CAR)
    result = enforcer.enforce_cmd(_cmd(0.5))
    assert result.linear.x == pytest.approx(0.0)


def test_half_distance_half_speed(enforcer):
    enforcer.update_distance(SAFE_DISTANCE_TO_CAR * 1.5)
    result = enforcer.enforce_cmd(_cmd(1.0))
    assert result.linear.x == pytest.approx(0.5)


def test_stale_distance_passes_cmd_unchanged(enforcer):
    enforcer.update_distance(SAFE_DISTANCE_TO_CAR)
    enforcer._last_update -= VEHICLE_STALE_SEC + 0.1
    result = enforcer.enforce_cmd(_cmd(0.5))
    assert result.linear.x == pytest.approx(0.5)
