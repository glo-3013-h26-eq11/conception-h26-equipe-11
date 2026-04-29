from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist
import time


class Enforcer(ABC):
    def __init__(self, priority=1):
        self.priority = priority
        self.last_real_speed_timer = None

    @abstractmethod
    def enforce_cmd(self, cmd: Twist) -> Twist:
        pass

    @abstractmethod
    def update_with_real_speed(self, real_cmd: Twist):
        pass

    def _compute_delta_time(self):
        if self.last_real_speed_timer is None:
            self.last_real_speed_timer = time.perf_counter()

        now = time.perf_counter()
        dt = now - self.last_real_speed_timer
        self.last_real_speed_timer = now

        return dt
