from yasmin import State
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.states.node_action_enum import NodeAction
from rclpy.node import Node
from navigation_interfaces.srv import GetNodeAction
import rclpy


class AtIntersectionToLoadState(State):
    def __init__(self, node: Node):
        super().__init__(
            outcomes=["left_turn", "forward_turn", "right_turn", "wait_load_zone"]
        )

        self.node = node

        self.outcome = None

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("AT_INTERSECTION_TO_LOAD state")

        blackboard["enforcers"] = [ImmobileEnforcer()]

        node_action = self.get_current_node_action()

        if node_action == NodeAction.LEFT_TURN:
            self.outcome = "left_turn"

        elif node_action == NodeAction.FORWARD_TURN:
            self.outcome = "forward_turn"

        elif node_action == NodeAction.RIGHT_TURN:
            self.outcome = "right_turn"

        elif node_action == NodeAction.WAIT_LOAD_ZONE:
            self.outcome = "wait_load_zone"

        else:
            blackboard["node"].get_logger().error(
                f"INVALID node action : {self.outcome}"
            )

        blackboard["node"].get_logger().info(f"Node action : {self.outcome}")

        return self.outcome

    def get_current_node_action(self) -> NodeAction:
        client = self.node.create_client(GetNodeAction, "get_node_action_load")

        if not client.wait_for_service(timeout_sec=5.0):
            self.node.get_logger().error("Service 'get_node_action_load' not available")
            raise RuntimeError("Service 'get_node_action_load' not available")

        request = GetNodeAction.Request()
        future = client.call_async(request)

        rclpy.spin_until_future_complete(self.node, future)

        if future.result() is not None:
            action_str = future.result().action
            return NodeAction(action_str)

        self.node.get_logger().error("Failed to get node action from service")
        raise RuntimeError("Failed to get node action from service")
