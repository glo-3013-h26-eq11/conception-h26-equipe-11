from central_manager.states.base_state import BaseState
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer


class InitialState(BaseState):
    def __init__(self, node):
        super().__init__(node, outcomes=["system_ready"])

    def execute(self, blackboard):
        self.node.get_logger().info("INITIAL state")
        blackboard["enforcers"] = [ImmobileEnforcer()]

        return self.spin_until_done(blackboard)

    def get_outcome(self, blackboard):
        if self._bb_get(blackboard, "rover_running", False):
            return "system_ready"
        return None

    def _should_restart_on_stop(self):
        return False