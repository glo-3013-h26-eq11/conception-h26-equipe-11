from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
from rclpy.node import Publisher
from proximity_sensor.merchandise_flag import MerchandiseFlag
import time

STOP_AFTER_DEPOSIT_DURATION = 1.5
STABLE_UNLOAD_DURATION = 1.0  # s
UNLOAD_CONFIRM_WINDOW = 0.3  # s — ignore LOADED noise after UNLOADED confirmed this long


class WaitAtDepositEnforcer(Enforcer):
    def __init__(self, deposit_over_publisher: Publisher):
        super().__init__()
        self.timer = 0.0
        self.merchandise_unloaded = False
        self.deposit_over_publisher = deposit_over_publisher
        self._published = False
        self._unloaded_time = None
        self._logger = None

    def update_with_real_speed(self, real_speed_cmd: Twist) -> None:
        if not self.merchandise_unloaded:
            return
        dt = self._compute_delta_time()
        self.timer += dt

    def enforce_cmd(self, cmd: Twist) -> Twist:
        if self._unloaded_time is not None and time.time() - self._unloaded_time > STABLE_UNLOAD_DURATION and not self._published:
            self.deposit_over_publisher.publish(String())
            self._published = True
            self.merchandise_unloaded = True
        enforced = Twist()
        if self._logger:
            self._logger.info(f"WaitAtDepositEnforcer: enforced cmd linear={enforced.linear.x:.2f}, angular={enforced.angular.z:.2f}")
        return enforced

    def merchandise_callback(self, msg: Bool) -> None:
        transition = MerchandiseFlag(msg.data)
        if transition == MerchandiseFlag.UNLOADED:
            if self._unloaded_time is None:
                self._unloaded_time = time.time()
        elif transition == MerchandiseFlag.LOADED:
            # Only reset if UNLOADED was very recent (< UNLOAD_CONFIRM_WINDOW).
            # After that threshold, treat LOADED as sensor noise — the
            # merchandise is considered gone and the rover must leave.
            if self._unloaded_time is not None and time.time() - self._unloaded_time < UNLOAD_CONFIRM_WINDOW:
                self._unloaded_time = None