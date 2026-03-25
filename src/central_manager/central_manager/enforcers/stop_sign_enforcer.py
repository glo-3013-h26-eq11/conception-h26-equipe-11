import time
from enum import Enum, auto
from typing import Optional
from geometry_msgs.msg import Twist
from central_manager.enforcers.base_enforcer import Enforcer

BRAKE_START_DIST: float = 1.0
STOP_TARGET_DIST: float = 0.61
STOP_DURATION: float = 1.0
STOP_IN_COOLDOWN_DURATION: float = 1.0
DISTANCE_STALE_SEC: float = 0.5
COOLDOWN_DURATION: float = 10.0


class _State(Enum):
    IDLE = auto()
    BRAKING = auto()
    STOPPED = auto()
    COOLDOWN = auto()


class StopSignEnforcer(Enforcer):
    def __init__(self, stop_duration: float = STOP_DURATION) -> None:
        super().__init__()
        self._state: _State = _State.IDLE
        self._stop_start: Optional[float] = None
        self._cooldown_start: Optional[float] = None
        self.stop_duration: float = stop_duration
        self._distance: Optional[float] = None
        self._last_update: float = 0.0
        self._logger = None
        self._has_triggered: bool = False
        self._last_processed_node_id: Optional[str] = None
        self._current_node_id: Optional[str] = None
        self._is_current_node_processed: bool = False

    def is_done(self) -> bool:
        if self._is_current_node_processed:
            return True
        if not self._has_triggered:
            return False
        return self._state == _State.IDLE or self._state == _State.COOLDOWN

    def is_transition_ready(self) -> bool:
        """True when it is safe to leave wall-following and decide intersection action."""
        if not self._has_triggered:
            return True

        if self._state == _State.COOLDOWN and self._cooldown_start is not None:
            return time.time() - self._cooldown_start >= STOP_IN_COOLDOWN_DURATION

        return False

    def update_distance(self, distance: Optional[float]) -> None:
        self._distance = distance
        self._last_update = time.time()

    def set_current_node_id(self, node_id: Optional[str]) -> None:
        previous_node_id = self._current_node_id
        self._current_node_id = node_id

        self._is_current_node_processed = (
            node_id is not None
            and self._last_processed_node_id is not None
            and node_id == self._last_processed_node_id
        )

        if previous_node_id != node_id:
            # New node reached; reset enforcer history so stop can trigger for a new node.
            self._has_triggered = False
            self._state = _State.IDLE
            self._stop_start = None
            self._cooldown_start = None

        if self._is_current_node_processed:
            # Re-entering same node that was previously stopped; keep done status for intersection state.
            self._has_triggered = True

    def update_with_real_speed(self, real_speed_cmd: Twist):
        pass

    def enforce_cmd(self, cmd: Twist) -> Twist:
        now = time.time()
        initial_command = cmd
        stale = (now - self._last_update) > DISTANCE_STALE_SEC
        d = None if stale else self._distance

        # If we're still at the same processed node, keep safe state and skip braking logic.
        if self._is_current_node_processed:
            if self._logger:
                self._logger.info(f"StopSignEnforcer: ignore already-processed node {self._current_node_id}")
            if self._state == _State.STOPPED or self._state == _State.COOLDOWN:
                return self.stop_robot(cmd)
            return cmd

        if self._has_triggered and (d is None or d > BRAKE_START_DIST) and self._state != _State.COOLDOWN:
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
                if self._logger:
                    self._logger.info(f"StopSignEnforcer: enforced cmd linear={cmd.linear.x:.2f}, angular={cmd.angular.z:.2f}")
                return cmd
            if d <= STOP_TARGET_DIST:
                self._state = _State.STOPPED
                self._stop_start = now
                self._log(f"ARRÊT — distance {d:.2f} m, pause {self.stop_duration:.1f}s")
                enforced = self.stop_robot(cmd)
                if self._logger:
                    self._logger.info(f"StopSignEnforcer: enforced cmd linear={enforced.linear.x:.2f}, angular={enforced.angular.z:.2f}")
                return enforced
            
            factor = (d - STOP_TARGET_DIST) / (BRAKE_START_DIST - STOP_TARGET_DIST)
            factor = max(0.0, min(1.0, factor))
            out = Twist()
            out.linear.x = max(cmd.linear.x * factor, 0.25)
            out.angular.z = cmd.angular.z
            if self._logger:
                self._logger.info(f"StopSignEnforcer: enforced cmd linear={out.linear.x:.2f}, angular={out.angular.z:.2f}")
            return out

        if self._state == _State.STOPPED:
            elapsed = now - self._stop_start
            if elapsed >= self.stop_duration:
                self._state = _State.COOLDOWN
                self._cooldown_start = now
                self._log("FIN STOP — mode COOLDOWN, wall follower peut reprendre")
                if self._logger:
                    self._logger.info(f"StopSignEnforcer: enforced cmd linear={cmd.linear.x:.2f}, angular={cmd.angular.z:.2f}")
                return cmd
            enforced = self.stop_robot(cmd)
            if self._logger:
                self._logger.info(f"StopSignEnforcer: enforced cmd linear={enforced.linear.x:.2f}, angular={enforced.angular.z:.2f}")
            return enforced

        if self._state == _State.COOLDOWN:
            elapsed = now - self._cooldown_start
            if elapsed >= COOLDOWN_DURATION:
                self._state = _State.IDLE
                self._has_triggered = False
                self._stop_start = None
                self._cooldown_start = None
                self._log("COOLDOWN terminé — retour IDLE")
                if self._logger:
                    self._logger.info(f"StopSignEnforcer: enforced cmd linear={initial_command.linear.x:.2f}, angular={initial_command.angular.z:.2f}")
                return initial_command
            elif elapsed < STOP_IN_COOLDOWN_DURATION:
                enforced = self.stop_robot(cmd)
                if self._logger:
                    self._logger.info(f"StopSignEnforcer: enforced cmd linear={enforced.linear.x:.2f}, angular={enforced.angular.z:.2f}")
                return enforced
            return cmd

        if self._logger:
            self._logger.info(f"StopSignEnforcer: enforced cmd linear={cmd.linear.x:.2f}, angular={cmd.angular.z:.2f}")
        return cmd

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            self._logger.info(msg)