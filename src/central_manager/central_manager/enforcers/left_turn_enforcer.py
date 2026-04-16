from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist

ARC_RADIUS = 0.230  # m
LEFT_TURN_SPEED = 0.4  # m/s


class LeftTurnEnforcer(Enforcer):
    def __init__(self):
        super().__init__(priority=1)
        self.steering_angle = LEFT_TURN_SPEED / ARC_RADIUS

    def update_with_real_speed(self, real_speed_cmd: Twist):
        pass

    def enforce_cmd(self, cmd: Twist) -> Twist:
        out = Twist()
        out.linear.x = LEFT_TURN_SPEED
        out.angular.z = self.steering_angle
        return out
