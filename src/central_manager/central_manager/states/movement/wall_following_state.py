from central_manager.states.base_state import BaseState
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer


class WallFollowingState(BaseState):
    def __init__(self, node):
        super().__init__(node, outcomes=["current_node_load", "current_node_deposit"])

    def execute(self, blackboard):
        self.node.get_logger().info("WALL_FOLLOWING_STATE state")

        stop_sign_enforcer = StopSignEnforcer()
        stop_sign_enforcer._logger = self.node.get_logger()

        current_node_id = self._bb_get(blackboard, "current_node_id", None)
        last_stop_node_id = self._bb_get(blackboard, "_last_stop_node_id", None)
        stop_sign_enforcer._last_processed_node_id = last_stop_node_id
        stop_sign_enforcer.set_current_node_id(current_node_id)

        car_follow_enforcer = CarFollowEnforcer()
        car_follow_enforcer._logger = self.node.get_logger()

        blackboard["enforcers"] = [stop_sign_enforcer, car_follow_enforcer]
        blackboard["_wf_stop_enforcer"] = stop_sign_enforcer

        return self.spin_until_done(blackboard)

    def get_outcome(self, blackboard):
        stop_enforcer: StopSignEnforcer = self._bb_get(blackboard, "_wf_stop_enforcer")
        current_node_id = self._bb_get(blackboard, "current_node_id")
        last_node = self._bb_get(blackboard, "_wf_last_node")

        if stop_enforcer and stop_enforcer.is_done() and current_node_id != last_node:
            blackboard["_wf_last_node"] = current_node_id
            blackboard["_last_stop_node_id"] = current_node_id

            immobile = ImmobileEnforcer()
            immobile._logger = self.node.get_logger()
            blackboard["enforcers"] = [immobile]

            route_mode = self._bb_get(blackboard, "route_mode", "load")
            if route_mode == "deposit":
                return "current_node_deposit"
            return "current_node_load"

        return None