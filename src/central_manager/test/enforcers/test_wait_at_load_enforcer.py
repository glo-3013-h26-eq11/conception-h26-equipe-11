import pytest
from central_manager.enforcers.wait_at_load_enforcer import WaitAtLoadEnforcer
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from unittest.mock import Mock
import time
from central_manager.enforcers.wait_at_load_enforcer import (
    STOP_AFTER_LOAD_DURATION,
)
from proximity_sensor.merchandise_flag import MerchandiseFlag


@pytest.fixture
def enforcer():
    mock_pub = Mock()
    return WaitAtLoadEnforcer(mock_pub)


def test_when_execute_then_twist_is_zero(enforcer):
    cmd_input = Twist()
    cmd_input.angular.x = 5.0
    cmd_input.angular.z = 5.0

    cmd_output = enforcer.enforce_cmd(cmd_input)

    cmd_expected = Twist()
    assert cmd_output == cmd_expected


def test_given_merchandise_loaded_when_update_then_stop_timer_counts(enforcer):
    cmd_input = Twist()
    merchandise_loaded = Bool()
    merchandise_loaded.data = MerchandiseFlag.LOADED.value
    enforcer.merchandise_callback(merchandise_loaded)

    # Wait for stability
    time.sleep(1.1)
    enforcer.merchandise_callback(merchandise_loaded)

    for _ in range(5):
        enforcer.update_with_real_speed(cmd_input)
        time.sleep(0.1)

    assert enforcer.timer != 0


def test_given_merchandise_loaded_when_wait_to_full_stop_then_publishes_deposit_over(
    enforcer,
):
    cmd_input = Twist()
    merchandise_loaded = Bool()
    merchandise_loaded.data = MerchandiseFlag.LOADED.value
    enforcer.merchandise_callback(merchandise_loaded)

    # With stability check, need to wait 1 second
    time.sleep(1.1)
    enforcer.merchandise_callback(merchandise_loaded)

    enforcer.enforce_cmd(cmd_input)

    enforcer.load_over_publisher.publish.assert_called()


def test_given_merchandise_still_unloaded_when_enforce_then_publisher_never_called(
    enforcer,
):
    cmd_input = Twist()

    # Send UNLOADED - should not trigger
    merchandise_unloaded = Bool()
    merchandise_unloaded.data = MerchandiseFlag.UNLOADED.value
    enforcer.merchandise_callback(merchandise_unloaded)

    for _ in range(5):
        enforcer.enforce_cmd(cmd_input)
        time.sleep(0.1)

    enforcer.load_over_publisher.publish.assert_not_called()


def test_given_merchandise_still_unloaded_when_update_then_stop_timer_is_zero(enforcer):
    cmd_input = Twist()

    for _ in range(5):
        enforcer.update_with_real_speed(cmd_input)
        time.sleep(0.1)

    assert enforcer.timer == 0
