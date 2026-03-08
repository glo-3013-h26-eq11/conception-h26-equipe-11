from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer

class CarFollowEnforcer(Enforcer):
    def __init__(self):
        self.min_follow_distance = 0.2  # m

    def car_follow(self, cmd: Twist, distance: float) -> Twist:
        speed_adjustment = (distance - self.min_follow_distance) / self.min_follow_distance
        cmd.linear.x = cmd.linear.x * max(0.0, min(1.0, speed_adjustment))
        return cmd