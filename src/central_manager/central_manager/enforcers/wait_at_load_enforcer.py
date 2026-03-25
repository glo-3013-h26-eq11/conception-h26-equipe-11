from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Publisher
from std_msgs.msg import String, Bool
from proximity_sensor.merchandise_flag import MerchandiseFlag
import time

STOP_AFTER_LOAD_DURATION = 1.5  # s
STABLE_LOAD_DURATION = 1.0  # s 


class WaitAtLoadEnforcer(Enforcer):
    def __init__(self, load_over_publisher: Publisher):
        super().__init__()
        self.timer = 0.0
        self.merchandise_loaded = False
        self.load_over_publisher = load_over_publisher
        self._published = False
        self._loaded_time = None
        self._logger = None

    def update_with_real_speed(self, real_speed_cmd: Twist) -> None:
        if not self.merchandise_loaded:
            return
        dt = self._compute_delta_time()
        self.timer += dt

    def enforce_cmd(self, cmd: Twist) -> Twist:
        if self._loaded_time is not None and time.time() - self._loaded_time > STABLE_LOAD_DURATION and not self._published:
            self.load_over_publisher.publish(String())
            self._published = True
            self.merchandise_loaded = True
        enforced = Twist()
        if self._logger:
            self._logger.info(f"WaitAtLoadEnforcer: enforced cmd linear={enforced.linear.x:.2f}, angular={enforced.angular.z:.2f}")
        return enforced

    def merchandise_callback(self, msg: Bool) -> None:
        transition = MerchandiseFlag(msg.data)
        if transition == MerchandiseFlag.LOADED:
            if self._loaded_time is None:
                self._loaded_time = time.time()
        elif transition == MerchandiseFlag.UNLOADED:
            self._loaded_time = None