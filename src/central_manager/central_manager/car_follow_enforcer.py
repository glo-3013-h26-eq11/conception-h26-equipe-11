import time
from typing import Optional
from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer

VEHICLE_STALE_SEC: float = 1.0


class CarFollowEnforcer(Enforcer):
    def __init__(self):
        self.min_follow_distance: float = 0.25
        self._follow_distance: Optional[float] = None
        self._last_update: float = 0.0
        self._logger = None

    def update_distance(self, distance: Optional[float]) -> None:
        self._follow_distance = distance
        self._last_update = time.time()

    def enforce_cmd(self, cmd: Twist) -> Twist:
        stale = (time.time() - self._last_update) > VEHICLE_STALE_SEC
        d = None if stale else self._follow_distance
        if d is None:
            return cmd
        factor = (d - self.min_follow_distance) / self.min_follow_distance
        factor = max(0.0, min(1.0, factor))
        if self._logger is not None:
            self._logger.info(f"Véhicule devant à {d:.2f} m — vitesse x{factor:.2f}")
        out = Twist()
        out.linear.x = cmd.linear.x * factor
        out.angular.z = cmd.angular.z * factor
        return out
