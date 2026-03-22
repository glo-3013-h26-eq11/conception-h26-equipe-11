import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from navigation.route_selector import RouteSelector
from central_manager.states.node_action_enum import NodeAction
from navigation_interfaces.srv import GetNodeAction


class RoutePlannerNode(Node):
    def __init__(self, route_selector: RouteSelector | None = None):
        super().__init__("route_planner_node")

        self._route_selector = route_selector

        self.subscription_current = self.create_subscription(
            String, "current_node", self.current_node_callback, 10
        )
        self.subscription_goal = self.create_subscription(
            String, "goal_node", self.goal_node_callback, 10
        )

        if route_selector is None:
            self.subscription_map = self.create_subscription(
                String, "map_manager/parsed_map_topic", self._map_callback, 10
            )

        self.publisher_directions = self.create_publisher(
            String, "route_plan/directions", 10
        )
        self.publisher_nodes = self.create_publisher(String, "route_plan/nodes", 10)

        self.get_node_action_service_load = self.create_service(
            GetNodeAction, "get_node_action_load", self.handle_get_node_action_load
        )

        self.get_node_action_service_deposit = self.create_service(
            GetNodeAction,
            "get_node_action_deposit",
            self.handle_get_node_action_deposit,
        )

        self.current_node: str | None = None
        self.goal_node: str | None = None
        self._current_directions: list | None = None
        self._node_at_last_publish: str | None = None

    def handle_get_node_action_load(self, request, response):
        response.action = NodeAction.LEFT_TURN.value
        return response

    def handle_get_node_action_deposit(self, request, response):
        response.action = NodeAction.LEFT_TURN.value
        return response

    def _map_callback(self, msg: String) -> None:
        if self._route_selector is not None:
            return

        try:
            map_dict = json.loads(msg.data)
            self._route_selector = RouteSelector(graph=map_dict)
            self.get_logger().info("Map received, route selector initialized.")

            self._try_compute_route()

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            self.get_logger().error(f"Failed to parse map: {e}")

    def current_node_callback(self, msg: String) -> None:
        self.current_node = msg.data.strip()
        self._try_compute_route()

    def goal_node_callback(self, msg: String) -> None:
        self.goal_node = msg.data.strip()
        self._current_directions = None
        self._node_at_last_publish = None
        self._try_compute_route()

    def _try_compute_route(self) -> None:
        if self._route_selector is None:
            return
        if self.current_node is None or not self.current_node:
            return
        if self.goal_node is None or not self.goal_node:
            return

        if (
            self._current_directions is None
            or self.current_node != self._node_at_last_publish
        ):
            self._publish_full_route()
            return

        if self._current_directions:
            self._republish_directions()

    def _publish_full_route(self) -> None:
        try:
            result = self._route_selector.compute_path(
                self.current_node, self.goal_node
            )
        except ValueError as e:
            self.get_logger().error(f"Route computation failed: {e}")
            return

        if result is None:
            nodes_path, directions_path = [], []
            self.get_logger().warning(
                f"No path found from '{self.current_node}' to '{self.goal_node}'."
            )
        else:
            nodes_path, directions_path = result

        self._current_directions = list(directions_path)

        msg_dirs = String()
        msg_dirs.data = json.dumps(directions_path)
        self.publisher_directions.publish(msg_dirs)

        msg_nodes = String()
        msg_nodes.data = json.dumps(nodes_path)
        self.publisher_nodes.publish(msg_nodes)
        self._node_at_last_publish = self.current_node

    def _republish_directions(self) -> None:
        msg_dirs = String()
        msg_dirs.data = json.dumps(self._current_directions)
        self.publisher_directions.publish(msg_dirs)

    def _publish_remaining_route(self) -> None:
        self._current_directions.pop(0)
        remaining = self._current_directions

        if not remaining:
            self._current_directions = []

        msg_dirs = String()
        msg_dirs.data = json.dumps(remaining)
        self.publisher_directions.publish(msg_dirs)
        self._node_at_last_publish = self.current_node


def main(args=None):
    rclpy.init(args=args)
    node = RoutePlannerNode(route_selector=None)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
