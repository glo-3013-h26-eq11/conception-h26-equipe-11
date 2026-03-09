from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer

class CarFollowEnforcer(Enforcer):
    def __init__(self):
        self.min_follow_distance = 0.2
        self.follow_distance: float | None = None

    def enforce_cmd(self, cmd: Twist) -> Twist:
        if self.follow_distance is None:
            return cmd
        return self.car_follow(cmd, self.follow_distance)

    def car_follow(self, cmd: Twist, distance: float) -> Twist:
        speed_adjustment = (distance - self.min_follow_distance) / self.min_follow_distance
        cmd.linear.x = cmd.linear.x * max(0.0, min(1.0, speed_adjustment))
        print(f"CarFollowEnforcer: distance={distance:.2f}, speed_adjustment={speed_adjustment:.2f}, new_speed={cmd.linear.x:.2f}")
        return cmd