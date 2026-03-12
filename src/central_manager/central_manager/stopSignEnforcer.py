import time
from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer


class StopSignEnforcer(Enforcer):
    def __init__(self):
        self.stop_detected: bool = False
        self.stop_start_time: float = None
        self.stop_duration: float = 1.5
        self.cool_down: float = 8.0
        self.cool_down_start: float = None

    @property
    def is_stopping(self) -> bool:
        return self.stop_start_time is not None

    @property
    def is_in_cooldown(self) -> bool:
        if self.cool_down_start is None:
            return False
        return time.time() - self.cool_down_start < self.cool_down

    def enforce_cmd(self, cmd: Twist) -> Twist:
        if self.stop_detected:
            if self.stop_start_time is None:
                self.stop_start_time = time.time()

            elapsed = time.time() - self.stop_start_time
            if elapsed < self.stop_duration:
                return self.stop_robot(cmd)
            else:
                self.stop_detected = False
                self.stop_start_time = None
                self.cool_down_start = time.time()
        return cmd

    def stop(self, cmd: Twist) -> Twist:
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        return cmd