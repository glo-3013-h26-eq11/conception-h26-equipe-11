from typing import Optional
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.states.node_action_enum import NodeAction
from navigation_interfaces.srv import GetNodeAction
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS
from central_manager.state_base import RoverState


class AtIntersectionToDepositState(RoverState):
    def __init__(self, node):
        self.node = node
        self.client = self.node.create_client(GetNodeAction, "get_node_action_deposit")
        self.outcome = None
        self._request_future = None

    def on_enter(self, blackboard):
        self.outcome = None
        self.node.get_logger().info("AT_INTERSECTION_TO_DEPOSIT state")
        blackboard[BLACKBOARD_ENFORCERS] = [ImmobileEnforcer()]
        self._request_future = None

        if not self.client.wait_for_service(timeout_sec=5.0):
            self.node.get_logger().error(
                "Service 'get_node_action_deposit' not available"
            )
            raise RuntimeError("Service 'get_node_action_deposit' not available")

        request = GetNodeAction.Request()
        self._request_future = self.client.call_async(request)
        self._request_future.add_done_callback(self._handle_service_response)

    def _handle_service_response(self, future):
        result = future.result()
        if result is None:
            self.node.get_logger().error("Failed to get node action from service")
            self.outcome = "back_to_init"
            return

        node_action = NodeAction(result.action)
        if node_action == NodeAction.LEFT_TURN:
            self.outcome = "left_turn"
        elif node_action == NodeAction.FORWARD_TURN:
            self.outcome = "forward_turn"
        elif node_action == NodeAction.WALL_FOLLOW:
            self.outcome = "right_turn"
        elif node_action == NodeAction.RIGHT_TURN:
            self.outcome = "right_turn"
        elif node_action == NodeAction.WAIT_DEPOSIT_ZONE:
            self.outcome = "wait_deposit_zone"
        elif node_action == NodeAction.BACK_TO_INIT:
            self.outcome = "back_to_init"
        else:
            self.node.get_logger().error(f"INVALID node action : {node_action}")
            self.outcome = "back_to_init"

        self.node.get_logger().info(f"Node action : {self.outcome}")

    def step(self, blackboard) -> Optional[str]:
        return self.outcome
