import pytest
from enforcers.merchandise_enforcer import MerchandiseEnforcer
from geometry_msgs.msg import Twist


@pytest.fixture
def enforcer():
    return MerchandiseEnforcer()


def test_given_loaded_merchandise_and_destination_zc_when_enforce_then_blocks(enforcer):
    # Arrange
    enforcer.load_detected = True
    enforcer.destination = "ZC1"

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.linear.z = 0.2
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.0
    assert result.angular.z == 0.0


def test_given_loaded_merchandise_and_destination_zd_when_enforce_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = True
    enforcer.destination = "ZD1"

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.2


def test_given_not_merchandise_loaded_and_destination_zc_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = False
    enforcer.destination = "ZC90"

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.2


def test_given_not_merchandise_loaded_and_destination_zd_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = False
    enforcer.destination = "ZD2"

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.2


def test_given_loaded_merchandise_and_destination_none_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = True
    enforcer.destination = None

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.0
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.0


def test_given_not_merchandise_loaded_and_destination_none_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = False
    enforcer.destination = None

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.0
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.0


def test_given_loaded_merchandise_and_destination_any_node_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = True
    enforcer.destination = "A1"

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.2
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.2


def test_given_not_merchandise_loaded_and_destination_any_node_then_allows(enforcer):
    # Arrange
    enforcer.load_detected = False
    enforcer.destination = "A4"

    # Act
    cmd = Twist()
    cmd.linear.x = 0.5
    cmd.angular.z = 0.0
    result = enforcer.enforce_cmd(cmd)

    # Assert
    assert result.linear.x == 0.5
    assert result.angular.z == 0.0
