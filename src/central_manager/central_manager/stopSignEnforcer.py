import time
from enum import Enum, auto
from typing import Optional
from geometry_msgs.msg import Twist
from central_manager.base_enforcer import Enforcer

BRAKE_START_DIST:    float = 1.0
STOP_TARGET_DIST:    float = 0.55
STOP_DURATION:       float = 1.5
DISTANCE_STALE_SEC:  float = 0.5
TURN_TIME: float = 1.4


class _State(Enum):
    IDLE     = auto()
    BRAKING  = auto()
    STOPPED  = auto()


class StopSignEnforcer(Enforcer):
    def __init__(self, stop_duration: float = STOP_DURATION) -> None:
        self._state: _State = _State.IDLE
        self._stop_start: Optional[float] = None

        self.stop_duration: float = stop_duration

        self._distance: Optional[float] = None
        self._last_update: float = 0.0

        self._logger = None

        self._has_triggered: bool = False

    def update_distance(self, distance: Optional[float]) -> None:
        self._distance = distance
        self._last_update = time.time()

    def enforce_cmd(self, cmd: Twist) -> Twist:
        now = time.time()

        stale = (now - self._last_update) > DISTANCE_STALE_SEC
        d = None if stale else self._distance

        if self._state == _State.IDLE and not self._has_triggered:
            if d is not None and d <= BRAKE_START_DIST:
                self._state = _State.BRAKING
                self._has_triggered = True
                self._log(f"STOP détecté à {d:.2f} m — freinage")

        if self._state == _State.BRAKING:
            if d is None:
                self._state = _State.IDLE
                self._has_triggered = False
                return cmd

            if d <= STOP_TARGET_DIST:
                self._state = _State.STOPPED
                self._stop_start = now
                self._log(
                    f"ARRÊT — distance {d:.2f} m, pause {self.stop_duration:.1f}s"
                )
                return self.stop_robot(cmd)

            factor = (d - STOP_TARGET_DIST) / (BRAKE_START_DIST - STOP_TARGET_DIST)
            factor = max(0.0, min(1.0, factor))

            out = Twist()
            out.linear.x = max(cmd.linear.x * factor, 0.25)
            return out

        if self._state == _State.STOPPED:
            elapsed = now - self._stop_start
            if elapsed >= STOP_DURATION:
                self._state = _State.IDLE
                self._has_triggered = False
                
                return cmd

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)