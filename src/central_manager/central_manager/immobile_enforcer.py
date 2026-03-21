from central_manager.base_enforcer import Enforcer
from geometry_msgs.msg import Twist


class ImmobileEnforcer(Enforcer):
    def __init__(self):
        pass

    def enforce_cmd(self, cmd: Twist) -> Twist:
        return Twist()
