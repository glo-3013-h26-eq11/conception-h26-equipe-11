import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
from navigation.route_selector import RouteSelector


class RoutePlannerNode(Node):
    def __init__(self):
        super().__init__("route_planner_node")
        self.route_selector = RouteSelector()
        self.subscription_current = self.create_subscription(
            String, "current_node", self.current_node_callback, 10
        )
        self.subscription_goal = self.create_subscription(
            String, "goal_node", self.goal_node_callback, 10
        )
        self.publisher_route = self.create_publisher(String, "route_plan", 10)
        self.current_node = None
        self.goal_node = None

    def current_node_callback(self, msg):
        self.current_node = msg.data
        self._try_compute_route()

    def goal_node_callback(self, msg):
        self.goal_node = msg.data
        self._try_compute_route()

    def _try_compute_route(self):
        if self.current_node is None or self.goal_node is None:
            return
        try:
            route = self.route_selector.compute_route(self.current_node, self.goal_node)
        except ValueError:
            return
        if route is None:
            return
        msg = String()
        msg.data = json.dumps(route)
        self.publisher_route.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    route_planner = RoutePlannerNode()
    rclpy.spin(route_planner)
    route_planner.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
