from typing import Optional
from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer


class StopSignEnforcer(Enforcer):
    BRAKE_START = 1.0
    STOP_AT = 0.61

    def __init__(self):
        self.approach_distance: Optional[float] = None

    def enforce_cmd(self, cmd: Twist) -> Twist:
        dist = self.approach_distance
        
        if dist is None or dist >= self.BRAKE_START:
            return cmd

        if dist <= self.STOP_AT:
            return Twist()
        
        factor = (dist - self.STOP_AT) / (self.BRAKE_START - self.STOP_AT)
        factor = max(0.0, min(1.0, factor))

        scaled = Twist()
        scaled.linear.x = cmd.linear.x * factor
        scaled.angular.z = cmd.angular.z
        return scaled