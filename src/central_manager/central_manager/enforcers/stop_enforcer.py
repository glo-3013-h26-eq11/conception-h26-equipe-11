from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist

STOP_DURATION = 1.5  # s


class StopEnforcer(Enforcer):
    def __init__(self):
        super().__init__()

        self.timer = 0

    def update_with_real_speed(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.timer += dt

    def enforce_cmd(self, cmd) -> Twist:
        if self.is_stop_over():
            return cmd
        else:
            return Twist()

    def is_stop_over(self):
        return self.timer >= STOP_DURATION
