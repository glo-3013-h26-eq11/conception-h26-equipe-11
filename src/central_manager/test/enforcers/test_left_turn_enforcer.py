import pytest
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from geometry_msgs.msg import Twist
from unittest.mock import Mock


@pytest.fixture
def enforcer():
    mock_pub = Mock()
    return LeftTurnEnforcer(mock_pub)


def test_given_arc_done_when_enforce_cmd_then_return_empty_twist(enforcer):
    enforcer.travel_distance_already_done = enforcer.total_distance_to_travel
    initial_command = Twist()
    initial_command.linear.x = 5.0
    initial_command.angular.z = 5.0

    resulting_command = enforcer.enforce_cmd(initial_command)

    assert resulting_command.linear.x == 0
    assert resulting_command.linear.y == 0


def test_given_travel_done_when_enforce_cmd_then_publish_turn_over(enforcer):
    enforcer.travel_distance_already_done = enforcer.total_distance_to_travel

    enforcer.enforce_cmd(Twist())

    enforcer.turn_over_publisher.publish.assert_called_once()


def test_given_arc_not_done_when_enforce_cmd_then_turn(enforcer):
    initial_command = Twist()

    resulting_command = enforcer.enforce_cmd(initial_command)

    assert resulting_command.linear.x != 0
    assert resulting_command.angular.z != 0


def test_when_update_real_speed_then_distance_already_done_is_updated(enforcer):
    real_speed_command = Twist()
    real_speed_command.linear.x = 0.4

    def mocked_compute_delta_time():
        return 0.2

    enforcer._compute_delta_time = mocked_compute_delta_time

    enforcer.update_with_real_speed(real_speed_command)

    assert enforcer.travel_distance_already_done == pytest.approx(0.2 * 0.4)
