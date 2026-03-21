from yasmin import State
from std_msgs.msg import String
from central_manager.immobile_enforcer import ImmobileEnforcer
from central_manager.states.node_action_enum import NodeAction


class AtIntersectionToDepositState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=["left_turn", "forward_turn", "right_turn", "wait_deposit_zone"]
        )

        self.outcome = None

    def execute(self, blackboard):

        blackboard["enforcers"] = [ImmobileEnforcer()]

        node_action = self.get_current_node_action()

        if node_action == NodeAction.LEFT_TURN:
            self.outcome = "left_turn"

        elif node_action == NodeAction.FORWARD_TURN:
            self.outcome = "forward_turn"

        elif node_action == NodeAction.RIGHT_TURN:
            self.outcome = "right_turn"

        elif node_action == NodeAction.WAIT_DEPOSIT_ZONE:
            self.outcome = "wait_deposit_zone"

        blackboard["node"].get_logger().info(f"Node action : {self.outcome}")

        return self.outcome

    def get_current_node_action(self) -> NodeAction:
        pass
