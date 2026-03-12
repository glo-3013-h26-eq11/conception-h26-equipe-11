import time
from enum import Enum, auto
from typing import Optional
from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer

BRAKE_START_DIST:    float = 1.0
STOP_TARGET_DIST:    float = 0.55
STOP_DURATION:       float = 1.5
COOLDOWN_DURATION:  float = 2.0
DISTANCE_STALE_SEC: float = 0.5


class _State(Enum):
    IDLE     = auto()
    BRAKING  = auto()
    STOPPED  = auto()
    COOLDOWN = auto()


class StopSignEnforcer(Enforcer):
    def __init__(self, stop_duration: float = STOP_DURATION) -> None:
        self._state: _State = _State.IDLE
        self._stop_start: Optional[float] = None
        self._cooldown_start: float = 0.0
        self.stop_duration: float = stop_duration
        self._distance: Optional[float] = None
        self._last_update: float = 0.0
        self._logger = None

    def update_distance(self, distance: Optional[float]) -> None:
        self._distance = distance
        self._last_update = time.time()

    def enforce_cmd(self, cmd: Twist) -> Twist:
        stale = (time.time() - self._last_update) > DISTANCE_STALE_SEC
        d = None if stale else self._distance

        if self._state == _State.IDLE:
            if d is not None and d <= BRAKE_START_DIST:
                self._state = _State.BRAKING
                self._log(f"Panneau STOP détecté à {d:.2f} m — freinage progressif")

        if self._state == _State.BRAKING:
            if d is None or d > BRAKE_START_DIST:
                self._state = _State.IDLE
                return cmd

            if d <= STOP_TARGET_DIST:
                self._state = _State.STOPPED
                self._stop_start = time.time()
                self._log(
                    f"ARRÊT au panneau STOP — distance {d:.2f} m, "
                    f"pause {self.stop_duration:.1f} s"
                )
                return self.stop_robot(cmd)

            factor = (d - STOP_TARGET_DIST) / (BRAKE_START_DIST - STOP_TARGET_DIST)
            factor = max(0.0, min(1.0, factor))
            out = Twist()
            out.linear.x  = max(cmd.linear.x * factor, 0.25)
            out.angular.z = cmd.angular.z
            return out

        if self._state == _State.STOPPED:
            elapsed = time.time() - self._stop_start
            if elapsed < self.stop_duration:
                return self.stop_robot(cmd)
            self._state = _State.COOLDOWN
            self._cooldown_start = time.time()
            self._log("Reprise — fin de pause au panneau STOP")

        if self._state == _State.COOLDOWN:
            if d is None or (time.time() - self._cooldown_start) > COOLDOWN_DURATION:
                self._state = _State.IDLE

        return cmd

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)