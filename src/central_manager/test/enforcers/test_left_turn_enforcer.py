import pytest
from central_manager.enforcers.left_turn_enforcer import LeftTurnEnforcer
from geometry_msgs.msg import Twist


@pytest.fixture
def enforcer():
    return LeftTurnEnforcer()



def test_given_arc_not_done_when_enforce_cmd_then_turn(enforcer):
    initial_command = Twist()

    resulting_command = enforcer.enforce_cmd(initial_command)

    assert resulting_command.linear.x != 0
    assert resulting_command.angular.z != 0

