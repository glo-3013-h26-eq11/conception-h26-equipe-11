import time
from enum import Enum, auto
from typing import Optional
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from central_manager.enforcers.base_enforcer import Enforcer
import math

BRAKE_START_DIST: float = 0.75
STOP_TARGET_DIST: float = 0.61
STOP_DURATION: float = 1.0
DISTANCE_STALE_SEC: float = 0.5

GOOD_ANGLE_ALIGNMENT_LEFT = -9.0
GOOD_ANGLE_ALIGNEMENT_RIGHT = 2.0

ANGLE_CORRECTION_SPEED = 0.7  # rad/s


class _State(Enum):
    IDLE = auto()
    BRAKING = auto()
    STOPPED = auto()
    ADJUST_ANGLE = auto()
    OVER = auto()


class StopSignEnforcer(Enforcer):
    def __init__(
        self, stop_over_publisher, stop_duration: float = STOP_DURATION, logger=None
    ) -> None:
        super().__init__()
        self._state: _State = _State.IDLE
        self._stop_start: Optional[float] = None

        self.stop_duration: float = stop_duration

        self.stop_over_publisher = stop_over_publisher

        self._distance: Optional[float] = None
        self._relative_angle = None
        self._last_update: float = 0.0

        self._logger = logger

        self._has_triggered: bool = False

    def is_done(self):
        if self._state == _State.IDLE or self._state == _State.OVER:
            return True
        else:
            return False

    def update_distance(self, distance: Optional[float]) -> None:
        self._distance = distance
        self._last_update = time.time()

    def update_relative_angle(self, relative_angle):
        self._relative_angle = relative_angle
        self._last_update = time.time()

    def update_with_real_speed(self, real_speed_cmd: Twist):
        dt = self._compute_delta_time()

        self.last_real_speed_timer += dt

    def correct_rover_left(self) -> Twist:
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = ANGLE_CORRECTION_SPEED
        return cmd

    def correct_rover_right(self) -> Twist:
        cmd = Twist()
        cmd.linear.x = 0.0
        cmd.angular.z = -ANGLE_CORRECTION_SPEED
        return cmd

    def is_rover_at_valid_angle_from_aruco(self):
        return (
            self._relative_angle > GOOD_ANGLE_ALIGNMENT_LEFT
            and self._relative_angle < GOOD_ANGLE_ALIGNEMENT_RIGHT
        )

    def enforce_cmd(self, cmd: Twist) -> Twist:
        now = time.time()
        stale = (now - self._last_update) > DISTANCE_STALE_SEC
        d = None if stale else self._distance

        if self._has_triggered and (d is None or d > BRAKE_START_DIST):
            self._has_triggered = False
            cmd = self.switch_state(_State.IDLE, cmd)

        if self._state == _State.IDLE and not self._has_triggered:
            if d is not None and d <= BRAKE_START_DIST:
                self._has_triggered = True

                cmd = self.switch_state(_State.BRAKING, cmd)

                self._log(f"STOP détecté à {d:.2f} m — freinage")

        if self._state == _State.BRAKING:
            if d is None:
                return cmd
            if d <= STOP_TARGET_DIST:
                self._stop_start = now
                self._log(
                    f"ARRÊT — distance {d:.2f} m, pause {self.stop_duration:.1f}s"
                )

                cmd = self.switch_state(_State.STOPPED, cmd)

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
                cmd = self.switch_state(_State.ADJUST_ANGLE, cmd)
                self._log("FIN STOP — mode ADJUST_ANGLE")

            return self.stop_robot(cmd)

        if self._state == _State.ADJUST_ANGLE:
            self._log(f"adjust state : _relative angle {self._relative_angle}")

            if self._relative_angle is None:
                return cmd

            if self._relative_angle < GOOD_ANGLE_ALIGNMENT_LEFT:
                cmd = self.correct_rover_right()
            elif self._relative_angle > GOOD_ANGLE_ALIGNEMENT_RIGHT:
                cmd = self.correct_rover_left()

            if self.is_rover_at_valid_angle_from_aruco():
                cmd = self.switch_state(_State.OVER, cmd)

        if self._state == _State.OVER:

            data = Bool()
            data.data = True
            self.stop_over_publisher.publish(data)

            return self.stop_robot(cmd)

        return cmd

    def switch_state(self, new_state:_State, cmd:Twist):
        self._state = new_state
        return self.enforce_cmd(cmd)

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)
