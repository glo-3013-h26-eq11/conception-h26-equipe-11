import json
import rclpy
from web_interface.system_health_node import HealthPingingNode
from std_msgs.msg import String
from navigation.goal_selector import GoalMode, GoalSelector
from navigation.route_selector import RouteSelector
from central_manager.states.node_action_enum import NodeAction
from navigation_interfaces.srv import GetNodeAction


class RoutePlannerNode(HealthPingingNode):
    def __init__(self, route_selector: RouteSelector | None = None):
        super().__init__("route_planner_node", "navigation")

        self._route_selector = route_selector
        self._goal_selector = GoalSelector(route_selector) if route_selector else None

        self.subscription_current = self.create_subscription(
            String, "current_node", self.current_node_id_distance_callback, 10
        )

        self.home_deposit_sub = self.create_subscription(
                String, "home_deposit_zone", self.set_home_deposit_callback, 10
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
        # Hardcode temporaire.
        # On va utiliser city_interface quand le reste sera stable.
        self.home_deposit_zone = None
        self.available_goals: list[str] = ["ZC1", "ZD1"]
        self.goal_mode: str = GoalMode.GO_LOAD.value

    def handle_get_node_action_load(self, _request, response):
        response.action = self._compute_node_action(
            mode=GoalMode.GO_LOAD, wait_action=NodeAction.WAIT_LOAD_ZONE
        )
        return response

    def handle_get_node_action_deposit(self, _request, response):
        response.action = self._compute_node_action(
            mode=GoalMode.GO_DEPOSIT, wait_action=NodeAction.WAIT_DEPOSIT_ZONE
        )
        return response

    def _map_callback(self, msg: String) -> None:
        if self._route_selector is not None:
            return

        try:
            map_dict = json.loads(msg.data)
            self._route_selector = RouteSelector(graph=map_dict)
            self._goal_selector = GoalSelector(self._route_selector)
            self.get_logger().info("Map received, route selector initialized.")

            self._try_compute_route()

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            self.get_logger().error(f"Failed to parse map: {e}")

    def set_home_deposit_callback(self, msg):
        self.home_deposit_zone = msg

    def current_node_id_distance_callback(self, msg: String) -> None:

        if self._route_selector is None:
            return

        data = json.loads(msg.data)

        tag = data.get("tag")

        self.current_node = self._route_selector.tag_to_id(tag)

        self._try_compute_route()

    def _compute_node_action(self, mode: GoalMode, wait_action: NodeAction) -> str:

        if self._route_selector is None:
            self.get_logger().error("Route selector is None")
            return NodeAction.BACK_TO_INIT.value

        if self.current_node is None or not self.current_node:
            self.get_logger().error("Current node is None")
            return NodeAction.BACK_TO_INIT.value

        self.goal_mode = mode.value

        goal_node = self._select_goal_for_mode(mode)
        result = self._route_selector.compute_path(self.current_node, goal_node)

        if result is None:
            return wait_action.value

        nodes_path, directions_path = result

        if len(directions_path) >= 1:

            msg_dirs = String()
            msg_dirs.data = json.dumps(directions_path)
            self.publisher_directions.publish(msg_dirs)

            msg_nodes = String()
            msg_nodes.data = json.dumps(nodes_path)
            self.publisher_nodes.publish(msg_nodes)

        if not directions_path:
            return wait_action.value

        direction_to_action = {
            "left": NodeAction.LEFT_TURN.value,
            "straight": NodeAction.FORWARD_TURN.value,
            "right": NodeAction.RIGHT_TURN.value,
        }
        next_direction = directions_path[0]

        # For points depots/chargement, selon la def du problème il faut aller "straight`,
        # mais techniquement wall follow devrait être l'action
        if "Z" in self.current_node:
            return NodeAction.WALL_FOLLOW.value

        return direction_to_action.get(next_direction, wait_action.value)

    def _select_goal_for_mode(self, mode: GoalMode) -> str:
        if self._route_selector is None:
            return self.current_node

        if self._goal_selector is None:
            self._goal_selector = GoalSelector(self._route_selector)

        selected = self._goal_selector.select_goal(
            current_node=self.current_node,
            available_goals=self.available_goals,
            mode=mode,
        )
        if selected is None:
            return self.current_node
        return selected

    def _try_compute_route(self) -> None:
        if self._route_selector is None:
            return
        if self.current_node is None or not self.current_node:
            return
        if not self.available_goals:
            return

        current_mode = GoalMode(self.goal_mode)
        wait_action = (
            NodeAction.WAIT_LOAD_ZONE
            if current_mode == GoalMode.GO_LOAD
            else NodeAction.WAIT_DEPOSIT_ZONE
        )
        self._compute_node_action(mode=current_mode, wait_action=wait_action)


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
