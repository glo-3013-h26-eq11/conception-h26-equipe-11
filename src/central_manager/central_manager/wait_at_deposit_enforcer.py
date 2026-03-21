from central_manager.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
import time

STOP_AFTER_DEPOSIT_DURATION = 1.5  # s


class WaitAtDepositEnforcer(Enforcer):
    def __init__(self):
        self.last_real_speed_timer = None
        self.timer = 0

    def update_timer(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.timer += dt

    def _compute_delta_time(self):
        if self.last_real_speed_timer is None:
            self.last_real_speed_timer = time.time()

        now = time.time()

        dt = now - self.last_real_speed_timer

        self.last_real_speed_timer = now

        return dt

    def enforce_cmd(self, cmd) -> Twist:
        if self.is_stop_after_deposit_over():
            return cmd
        else:
            return Twist()

    def is_stop_after_deposit_over(self):
        return self.timer >= STOP_AFTER_DEPOSIT_DURATION
