import time

from central_manager.states.base_state import BaseState
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.states.node_action_enum import NodeAction
from navigation_interfaces.srv import GetNodeAction
import rclpy


class AtIntersectionToDepositState(BaseState):
    def __init__(self, node):
        super().__init__(node, outcomes=["left_turn", "forward_turn", "right_turn", "wait_deposit_zone"])

        self.client = self.node.create_client(GetNodeAction, "get_node_action_deposit")

    def execute(self, blackboard):
        self.node.get_logger().info("AT_INTERSECTION_TO_DEPOSIT state")

        stop_enforcer = StopSignEnforcer()
        stop_enforcer._logger = self.node.get_logger()
        immobile_enforcer = ImmobileEnforcer()
        immobile_enforcer._logger = self.node.get_logger()

        current_node_id = self._bb_get(blackboard, "current_node_id", None)
        last_stop_node_id = self._bb_get(blackboard, "_last_stop_node_id", None)
        stop_enforcer._last_processed_node_id = last_stop_node_id
        stop_enforcer.set_current_node_id(current_node_id)

        # Keep immobile as final stage during stop-handling and route decision wait
        blackboard["enforcers"] = [stop_enforcer, immobile_enforcer]

        while not stop_enforcer.is_done():
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if not self._bb_get(blackboard, "rover_running", True):
                return "back_to_init"

        if stop_enforcer._has_triggered:
            blackboard["_last_stop_node_id"] = current_node_id

        # Keep the rover immobilized while we get the node action
        blackboard["enforcers"] = [immobile_enforcer]

        node_action = self._get_current_node_action()
        self.node.get_logger().info(f"Node action: {node_action}")

        action_map = {
            NodeAction.LEFT_TURN: "left_turn",
            NodeAction.FORWARD_TURN: "forward_turn",
            NodeAction.RIGHT_TURN: "right_turn",
            NodeAction.WALL_FOLLOW: "right_turn",
            NodeAction.WAIT_DEPOSIT_ZONE: "wait_deposit_zone",
        }

        outcome = action_map.get(node_action)
        if outcome is None:
            self.node.get_logger().error(f"INVALID node action: {node_action}")
            return "back_to_init"

        return outcome

    def _get_current_node_action(self) -> NodeAction:
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.node.get_logger().error("Service 'get_node_action_deposit' not available")
            raise RuntimeError("Service 'get_node_action_deposit' not available")

        request = GetNodeAction.Request()
        future = self.client.call_async(request)

        timeout = 10.0
        start = time.time()
        while rclpy.ok() and not future.done():
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if time.time() - start > timeout:
                self.node.get_logger().error("Timeout waiting for node action response")
                raise RuntimeError("Timeout waiting for node action response")

        result = future.result()
        if result is not None:
            return NodeAction(result.action)

        self.node.get_logger().error("Failed to get node action from service")
        raise RuntimeError("Failed to get node action from service")