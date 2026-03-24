from yasmin import State
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer
from central_manager.states.node_action_enum import NodeAction
import rclpy
from navigation_interfaces.srv import GetNodeAction
from std_msgs.msg import Bool


class AtIntersectionToDepositState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "left_turn",
                "forward_turn",
                "right_turn",
                "wait_deposit_zone",
                "back_to_init",
            ]
        )

        self.node = node

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.client = self.node.create_client(GetNodeAction, "get_node_action_deposit")

        self.outcome = None

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("AT_INTERSECTION_TO_DEPOSIT state")

        blackboard["enforcers"] = [ImmobileEnforcer()]

        node_action = self.get_current_node_action()

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
            self.node.get_logger().error(f"INVALID node action : {self.outcome}")

        self.node.get_logger().info(f"Node action : {self.outcome}")

        return self.outcome

    def get_current_node_action(self) -> NodeAction:
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.node.get_logger().error(
                "Service 'get_node_action_deposit' not available"
            )
            raise RuntimeError("Service 'get_node_action_deposit' not available")

        request = GetNodeAction.Request()
        future = self.client.call_async(request)

        while not future.done():
            rclpy.spin_once(self.node, timeout_sec=0.1)

        result = future.result()
        if result is not None:
            return NodeAction(result.action)

        self.node.get_logger().error("Failed to get node action from service")
        raise RuntimeError("Failed to get node action from service")
