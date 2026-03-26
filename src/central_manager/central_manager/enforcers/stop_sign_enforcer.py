import time
from enum import Enum, auto
from typing import Optional
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from central_manager.enforcers.base_enforcer import Enforcer

BRAKE_START_DIST: float = 0.75
STOP_TARGET_DIST: float = 0.61
STOP_DURATION: float = 1.0
DISTANCE_STALE_SEC: float = 0.5


class _State(Enum):
    IDLE = auto()
    BRAKING = auto()
    STOPPED = auto()
    COOLDOWN = auto()


class StopSignEnforcer(Enforcer):
    def __init__(
        self, stop_over_publisher, stop_duration: float = STOP_DURATION, logger=None
    ) -> None:
        super().__init__()
        self._state: _State = _State.IDLE
        self._stop_start: Optional[float] = None
        self._cooldown_start: Optional[float] = None

        self.stop_duration: float = stop_duration

        self.stop_over_publisher = stop_over_publisher

        self._distance: Optional[float] = None
        self._last_update: float = 0.0

        self._logger = logger

        self._has_triggered: bool = False

    def is_done(self):
        if self._state == _State.IDLE or self._state == _State.COOLDOWN:
            return True
        else:
            return False

    def update_distance(self, distance: Optional[float]) -> None:
        self._distance = distance
        self._last_update = time.time()

    def update_with_real_speed(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.last_real_speed_timer += dt

    def enforce_cmd(self, cmd: Twist) -> Twist:
        now = time.time()
        initial_command = cmd
        stale = (now - self._last_update) > DISTANCE_STALE_SEC
        d = None if stale else self._distance

        if self._has_triggered and (d is None or d > BRAKE_START_DIST):
            self._has_triggered = False
            self._state = _State.IDLE
            self._cooldown_start = None

        if self._state == _State.IDLE and not self._has_triggered:
            if d is not None and d <= BRAKE_START_DIST:
                self._state = _State.BRAKING
                self._has_triggered = True
                self._log(f"STOP détecté à {d:.2f} m — freinage")

        if self._state == _State.BRAKING:
            if d is None:
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
            out.angular.z = cmd.angular.z
            return out

        if self._state == _State.STOPPED:
            elapsed = now - self._stop_start
            if elapsed >= self.stop_duration:
                self._state = _State.COOLDOWN
                self._cooldown_start = now
                self._log("FIN STOP — mode COOLDOWN, wall follower peut reprendre")

                print("FIN STOP")

                data = Bool()
                data.data = True

                self.stop_over_publisher.publish(data)

            return self.stop_robot(cmd)

        return cmd

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)
