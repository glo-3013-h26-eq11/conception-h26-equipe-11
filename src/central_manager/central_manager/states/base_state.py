from yasmin import State
import rclpy


class BaseState(State):
    """
    Base class for all states.
    - No topic subscriptions (all subscriptions live in EnforcerManagerNode)
    - Provides helpers to read/write the shared blackboard
    - Provides active guard so callbacks only fire for the currently running state
    """

    def __init__(self, node, outcomes: list):
        super().__init__(outcomes=outcomes + ["back_to_init"])
        self.node = node

    def spin_until_done(self, blackboard):
        """Spin until get_outcome(blackboard) returns a non-None outcome string."""
        while True:
            rclpy.spin_once(self.node, timeout_sec=0.1)

            if not self._bb_get(blackboard, "rover_running", True):
                if self._should_restart_on_stop():
                    return "back_to_init"
                else:
                    continue

            outcome = self.get_outcome(blackboard)
            if outcome is not None:
                return outcome

    def _should_restart_on_stop(self):
        """Override in subclasses to customize behavior when rover is stopped."""
        return True

    def get_outcome(self, blackboard):
        """Override in subclasses. Return an outcome string or None to keep waiting."""
        return None

    @staticmethod
    def _bb_get(blackboard, key: str, default=None):
        """Blackboard.get() does not support defaults — use this wrapper instead."""
        try:
            return blackboard[key]
        except (KeyError, RuntimeError):
            return default