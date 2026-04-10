import time
from enum import Enum, auto
from typing import Optional
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from central_manager.enforcers.base_enforcer import Enforcer

BRAKE_START_DIST: float = 0.75
STOP_TARGET_DIST: float = 0.61
STOP_DURATION: float = 1.0
DISTANCE_STALE_SEC: float = 0.3

MAX_BREAKING_SPEED = 0.1

GOOD_ANGLE_ALIGNMENT_LEFT = -13.0
GOOD_ANGLE_ALIGNEMENT_RIGHT = -3.0

ANGLE_CORRECTION_SPEED = 0.5  # rad/s


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

    def is_done(self):
        if self._state == _State.OVER:
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
            self._relative_angle is not None
            and self._relative_angle > GOOD_ANGLE_ALIGNMENT_LEFT
            and self._relative_angle < GOOD_ANGLE_ALIGNEMENT_RIGHT
        )

    def _apply_braking_angle_correction(self, cmd: Twist) -> Twist:
        if self._relative_angle is None:
            return cmd

        if self._relative_angle < GOOD_ANGLE_ALIGNMENT_LEFT:
            cmd.angular.z = -ANGLE_CORRECTION_SPEED
        elif self._relative_angle > GOOD_ANGLE_ALIGNEMENT_RIGHT:
            cmd.angular.z = ANGLE_CORRECTION_SPEED
        else:
            cmd.angular.z = 0.0

        return cmd

    def stop_robot(self) -> Twist:
        return Twist()

    def enforce_cmd(self, cmd: Twist) -> Twist:

        now = time.time()
        stale = (now - self._last_update) > DISTANCE_STALE_SEC

        if stale:
            self._state = _State.IDLE
            self._distance = None

        if self._state == _State.IDLE:
            if self._distance is not None and self._distance <= BRAKE_START_DIST:
                self.switch_state(_State.BRAKING)
                self._log(f"STOP détecté à {self._distance:.2f} m — freinage")

        if self._state == _State.BRAKING:
            if self._distance is not None and self._distance <= STOP_TARGET_DIST:
                self._stop_start = now
                self._log(
                    f"ARRÊT — distance {self._distance:.2f} m, pause {self.stop_duration:.1f}s"
                )

                self.switch_state(_State.STOPPED)
                cmd = self.stop_robot()
            elif self._distance is not None:
                factor = (self._distance - STOP_TARGET_DIST) / (
                    BRAKE_START_DIST - STOP_TARGET_DIST
                )
                factor = max(0.0, min(1.0, factor))

                
                cmd.linear.x = max(cmd.linear.x * factor, MAX_BREAKING_SPEED)
                cmd.angular.z = 0.0
                cmd = self._apply_braking_angle_correction(cmd)

        if self._state == _State.STOPPED:
            elapsed = now - self._stop_start
            if elapsed >= self.stop_duration:
                self.switch_state(_State.OVER)
                self._log("FIN STOP — OVER")

            cmd = self.stop_robot()

        if self._state == _State.ADJUST_ANGLE:
            self._log(f"ADJUST : {self._relative_angle} deg")

            if self._relative_angle is not None:

                if self._relative_angle < GOOD_ANGLE_ALIGNMENT_LEFT:
                    self._log("CORRECT RIGHT")

                    cmd = self.correct_rover_right()

                elif self._relative_angle > GOOD_ANGLE_ALIGNEMENT_RIGHT:
                    self._log("CORRECT LEFT")

                    cmd = self.correct_rover_left()

                else:
                    self._log("NO CORRECTION")

                    cmd = self.stop_robot()

                if self.is_rover_at_valid_angle_from_aruco():
                    cmd = self.switch_state(_State.OVER)
            else:
                cmd = self.stop_robot()

        if self._state == _State.OVER:
            self._log("STOP OVER")
            data = Bool()
            data.data = True
            self.stop_over_publisher.publish(data)
            cmd = self.stop_robot()

        return cmd

    def switch_state(self, new_state: _State):
        self._state = new_state

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)
