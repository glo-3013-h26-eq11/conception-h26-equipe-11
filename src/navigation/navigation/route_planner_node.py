import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from navigation.route_selector import RouteSelector


class RoutePlannerNode(Node):
    def __init__(self, route_selector: RouteSelector):
        super().__init__("route_planner_node")
        self.route_selector = route_selector

        self.subscription_current = self.create_subscription(
            String, "current_node", self.current_node_callback, 10
        )
        self.subscription_goal = self.create_subscription(
            String, "goal_node", self.goal_node_callback, 10
        )

        self.publisher_directions = self.create_publisher(
            String, "route_plan/directions", 10
        )
        self.publisher_nodes = self.create_publisher(String, "route_plan/nodes", 10)

        self.current_node: str | None = None
        self.goal_node: str | None = None

    def current_node_callback(self, msg: String):
        self.current_node = msg.data
        self._try_compute_route()

    def goal_node_callback(self, msg: String):
        self.goal_node = msg.data
        self._try_compute_route()

    def _try_compute_route(self):
        if self.current_node is None or self.goal_node is None:
            return

        result = self.route_selector.compute_path(self.current_node, self.goal_node)

        if result is None:
            nodes_path, directions_path = [], []
        else:
            nodes_path, directions_path = result

        msg_dirs = String()
        msg_dirs.data = json.dumps(directions_path)
        self.publisher_directions.publish(msg_dirs)

        msg_nodes = String()
        msg_nodes.data = json.dumps(nodes_path)
        self.publisher_nodes.publish(msg_nodes)


def main(args=None):
    rclpy.init(args=args)

    TEMP_GRAPH = {
        "A1": {"g": "ZC1", "l": "A4", "d": "ZD1"},
        "A2": {"g": "A4", "l": "ZD1", "d": "A2"},
        "A3": {"g": "ZD1", "l": "A2", "d": "ZC1"},
        "A4": {"g": "A2", "l": "ZC1", "d": "A4"},
        "ZC1": {"l": "A1"},
        "ZD1": {"l": "A3"},
    }
    route_selector = RouteSelector(graph=TEMP_GRAPH)

    node = RoutePlannerNode(route_selector=route_selector)
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
