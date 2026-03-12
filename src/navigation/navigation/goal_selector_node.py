import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from navigation.goal_selector import GoalMode, GoalSelector
from navigation.route_selector import RouteSelector


class GoalSelectorNode(Node):
    def __init__(self, route_selector: RouteSelector | None = None):
        super().__init__("goal_selector_node")

        self._route_selector = route_selector
        self._goal_selector = GoalSelector(route_selector) if route_selector else None

        if route_selector is None:
            self._subscription_map = self.create_subscription(
                String,
                "map_manager/parsed_map_topic",
                self._map_callback,
                10,
            )

        self._subscription_current = self.create_subscription(
            String, "current_node", self._current_callback, 10
        )
        self._subscription_available_goals = self.create_subscription(
            String, "available_goals", self._available_goals_callback, 10
        )
        self._subscription_goal_mode = self.create_subscription(
            String, "goal_mode", self._goal_mode_callback, 10
        )

        self._publisher_goal = self.create_publisher(String, "goal_node", 10)

        self._current_node: str | None = None
        self._available_goals: list[str] = []
        self._goal_mode: str = GoalMode.GO_LOAD.value

        self._active_goal: str | None = None

    def _map_callback(self, msg: String) -> None:
        if self._route_selector is not None:
            return

        try:
            map_dict = json.loads(msg.data)
            self._route_selector = RouteSelector(graph=map_dict)
            self._goal_selector = GoalSelector(self._route_selector)
            self.get_logger().info("Map received, GoalSelector initialized.")

            self._try_select_and_publish()

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            self.get_logger().error(f"Failed to parse map: {e}")

    def _current_callback(self, msg: String) -> None:
        self._current_node = msg.data.strip()

    def _available_goals_callback(self, msg: String) -> None:
        try:
            parsed = json.loads(msg.data)
            if isinstance(parsed, list):
                self._available_goals = [
                    str(goal).strip() for goal in parsed if str(goal).strip()
                ]
            else:
                self.get_logger().warning("available_goals is not a JSON list.")
                self._available_goals = []
        except json.JSONDecodeError:
            self.get_logger().warning("Failed to decode available_goals JSON.")
            self._available_goals = []

        if self._active_goal is None:
            self._try_select_and_publish()

    def _goal_mode_callback(self, msg: String) -> None:
        new_mode = msg.data.strip()

        if new_mode not in (GoalMode.GO_LOAD.value, GoalMode.GO_DROP.value):
            self.get_logger().warning(f"Invalid goal_mode received: {new_mode}")
            return

        if new_mode != self._goal_mode:
            self._goal_mode = new_mode
            self._active_goal = None
            self.get_logger().info(f"Goal mode changed to: {self._goal_mode}")
            self._try_select_and_publish()

    def _try_select_and_publish(self) -> None:
        if self._goal_selector is None:
            return

        if self._current_node is None or not self._current_node:
            return

        if not self._available_goals:
            return

        if self._goal_mode not in (GoalMode.GO_LOAD.value, GoalMode.GO_DROP.value):
            self.get_logger().warning(f"Invalid goal_mode: {self._goal_mode}")
            return

        if self._active_goal is not None:
            return

        try:
            selected = self._goal_selector.select_goal(
                self._current_node,
                self._available_goals,
                mode=self._goal_mode,
            )
        except ValueError as e:
            self.get_logger().error(f"Goal selection failed: {e}")
            return

        if selected is None:
            self.get_logger().warning(
                "No reachable goal found for the current mode and available goals."
            )
            return

        self._active_goal = selected

        out_msg = String()
        out_msg.data = selected
        self._publisher_goal.publish(out_msg)

        self.get_logger().info(f"Published selected goal: {selected}")


def main(args=None):
    rclpy.init(args=args)
    node = GoalSelectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()