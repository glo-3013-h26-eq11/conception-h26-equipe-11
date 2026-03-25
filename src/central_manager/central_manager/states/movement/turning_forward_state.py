from central_manager.states.base_state import BaseState
from central_manager.enforcers.forward_turn_enforcer import ForwardTurnEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer


class TurningForwardState(BaseState):
    def __init__(self, node):
        super().__init__(node, outcomes=["turn_over"])

    def execute(self, blackboard):
        self.node.get_logger().info("TURNING_FORWARD state")

        blackboard["turn_over"] = False  # reset flag
        forward_turn_enforcer = ForwardTurnEnforcer(self.node.turn_over_publisher)
        forward_turn_enforcer._logger = self.node.get_logger()
        car_follow_enforcer = CarFollowEnforcer()
        car_follow_enforcer._logger = self.node.get_logger()
        stop_sign_enforcer = StopSignEnforcer()
        stop_sign_enforcer._logger = self.node.get_logger()
        blackboard["enforcers"] = [
            forward_turn_enforcer,
            car_follow_enforcer,
            stop_sign_enforcer,
        ]

        return self.spin_until_done(blackboard)

    def get_outcome(self, blackboard):
        if self._bb_get(blackboard, "turn_over", False):
            return "turn_over"
        return None