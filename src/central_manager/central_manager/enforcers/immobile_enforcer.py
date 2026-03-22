from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist


class ImmobileEnforcer(Enforcer):
    def __init__(self):
        pass

    def enforce_cmd(self, cmd: Twist) -> Twist:
        return Twist()

    def update_with_real_speed(self, real_cmd):
        pass
