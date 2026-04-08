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
            self._relative_angle > GOOD_ANGLE_ALIGNMENT_LEFT
            and self._relative_angle < GOOD_ANGLE_ALIGNEMENT_RIGHT
        )

    def stop_robot(self) -> Twist:
        return Twist()

    def enforce_cmd(self, cmd: Twist) -> Twist:
        
        self._log(f"state : {self._state}")
        
        now = time.time()
        stale = (now - self._last_update) > DISTANCE_STALE_SEC
        d = None if stale else self._distance

        if self._state == _State.IDLE:
            if d is not None and d <= BRAKE_START_DIST:
                self.switch_state(_State.BRAKING)
                self._log(f"STOP détecté à {d:.2f} m — freinage")

        if self._state == _State.BRAKING:
            if d is not None and d <= STOP_TARGET_DIST:
                self._stop_start = now
                self._log(
                    f"ARRÊT — distance {d:.2f} m, pause {self.stop_duration:.1f}s"
                )

                self.switch_state(_State.STOPPED)
                cmd = self.stop_robot()

            if d is not None:
                factor = (d - STOP_TARGET_DIST) / (BRAKE_START_DIST - STOP_TARGET_DIST)
                factor = max(0.0, min(1.0, factor))

                cmd.linear.x = max(cmd.linear.x * factor, 0.25)
                cmd.angular.z = 0.0 # Important pour ne pas perdre le Aruco

        if self._state == _State.STOPPED:
            elapsed = now - self._stop_start
            if elapsed >= self.stop_duration:
                self.switch_state(_State.ADJUST_ANGLE)
                self._log("FIN STOP — mode ADJUST_ANGLE")

            cmd = self.stop_robot()

        if self._state == _State.ADJUST_ANGLE:
            self._log(f"ADJUST : {self._relative_angle} deg")

            if self._relative_angle is not None:

                if self._relative_angle < GOOD_ANGLE_ALIGNMENT_LEFT:
                    self._log(f"CORRECT RIGHT")

                    cmd = self.correct_rover_right()

                elif self._relative_angle > GOOD_ANGLE_ALIGNEMENT_RIGHT:
                    self._log(f"CORRECT LEFT")

                    cmd = self.correct_rover_left()
                
                else:
                    self._log(f"NO CORRECTION")
                    
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

    def switch_state(self, new_state:_State):
        self._state = new_state

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)
