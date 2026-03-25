from central_manager.states.base_state import BaseState
from central_manager.enforcers.wait_at_load_enforcer import WaitAtLoadEnforcer


class AtLoadZoneToLoad(BaseState):
    def __init__(self, node):
        super().__init__(node, outcomes=["load_over"])

    def execute(self, blackboard):
        self.node.get_logger().info("WAIT_AT_LOAD_ZONE state")

        blackboard["load_over"] = False
        blackboard["merchandise_loaded"] = False

        wait_enforcer = WaitAtLoadEnforcer(self.node.load_over_publisher)
        wait_enforcer._logger = self.node.get_logger()
        blackboard["enforcers"] = [wait_enforcer]
        return self.spin_until_done(blackboard)

    def get_outcome(self, blackboard):
        if self._bb_get(blackboard, "load_over", False):
            blackboard["route_mode"] = "deposit"
            blackboard["merchandise_loaded"] = True
            return "load_over"
        return None