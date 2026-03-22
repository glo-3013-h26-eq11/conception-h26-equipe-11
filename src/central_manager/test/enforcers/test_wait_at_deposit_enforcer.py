import pytest
from central_manager.enforcers.wait_at_deposit_enforcer import WaitAtDepositEnforcer
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from unittest.mock import Mock
import time
from central_manager.enforcers.wait_at_deposit_enforcer import (
    STOP_AFTER_DEPOSIT_DURATION,
)
from proximity_sensor.merchandise_flag import MerchandiseFlag


@pytest.fixture
def enforcer():
    mock_pub = Mock()
    return WaitAtDepositEnforcer(mock_pub)


def test_when_execute_then_twist_is_zero(enforcer):
    cmd_input = Twist()
    cmd_input.angular.x = 5.0
    cmd_input.angular.z = 5.0

    cmd_output = enforcer.enforce_cmd(cmd_input)

    cmd_expected = Twist()
    assert cmd_output == cmd_expected


def test_given_merchandise_unloaded_when_update_then_stop_timer_counts(enforcer):
    cmd_input = Twist()
    merchandise_unloaded = Bool()
    merchandise_unloaded.data = MerchandiseFlag.UNLOADED.value
    enforcer.merchandise_callback(merchandise_unloaded)

    for _ in range(5):
        enforcer.update_with_real_speed(cmd_input)
        time.sleep(0.1)

    assert enforcer.timer != 0


def test_given_merchandise_unloaded_when_wait_to_full_stop_then_publishes_deposit_over(
    enforcer,
):
    cmd_input = Twist()
    merchandise_unloaded = Bool()
    merchandise_unloaded.data = MerchandiseFlag.UNLOADED.value
    enforcer.merchandise_callback(merchandise_unloaded)

    increments = int(STOP_AFTER_DEPOSIT_DURATION / 0.1 + 1)
    for _ in range(increments):
        enforcer.update_with_real_speed(cmd_input)
        time.sleep(0.1)
    enforcer.enforce_cmd(cmd_input)

    enforcer.deposit_over_publisher.publish.assert_called()


def test_given_merchandise_still_loaded_when_enforce_then_publisher_never_called(
    enforcer,
):
    cmd_input = Twist()

    for _ in range(5):
        enforcer.enforce_cmd(cmd_input)
        time.sleep(0.1)

    enforcer.deposit_over_publisher.publish.assert_not_called()


def test_given_merchandise_still_loaded_when_update_then_stop_timer_is_zero(enforcer):
    cmd_input = Twist()

    for _ in range(5):
        enforcer.update_with_real_speed(cmd_input)
        time.sleep(0.1)

    assert enforcer.timer == 0
