from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist


class ImmobileEnforcer(Enforcer):
    def __init__(self):
        super().__init__()
        self._logger = None

    def is_done(self) -> bool:
        return True

    def enforce_cmd(self, cmd: Twist) -> Twist:
        enforced = Twist()
        if self._logger:
            self._logger.info(f"ImmobileEnforcer: enforced cmd linear={enforced.linear.x:.2f}, angular={enforced.angular.z:.2f}")
        return enforced

    def update_with_real_speed(self, real_cmd: Twist) -> None:
        pass