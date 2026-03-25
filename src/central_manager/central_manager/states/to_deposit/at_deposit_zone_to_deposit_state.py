from central_manager.states.base_state import BaseState
from central_manager.enforcers.wait_at_deposit_enforcer import WaitAtDepositEnforcer


class AtDepositZoneToDeposit(BaseState):
    def __init__(self, node):
        super().__init__(node, outcomes=["deposit_over"])

    def execute(self, blackboard):
        self.node.get_logger().info("WAIT_AT_DEPOSIT_ZONE state")

        blackboard["deposit_over"] = False
        blackboard["merchandise_loaded"] = False

        wait_enforcer = WaitAtDepositEnforcer(self.node.deposit_over_publisher)
        wait_enforcer._logger = self.node.get_logger()
        blackboard["enforcers"] = [wait_enforcer]

        return self.spin_until_done(blackboard)

    def get_outcome(self, blackboard):
        if self._bb_get(blackboard, "deposit_over", False):
            blackboard["route_mode"] = "load"
            blackboard["merchandise_loaded"] = False
            return "deposit_over"
        return None