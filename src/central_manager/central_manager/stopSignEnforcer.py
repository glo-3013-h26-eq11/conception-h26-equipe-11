import time
from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer


class StopSignEnforcer(Enforcer):
    def __init__(self):
        self.stop_detected: bool = False
        self.stop_start_time: float = None
        self.stop_duration: float = 1.5

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
        return cmd
