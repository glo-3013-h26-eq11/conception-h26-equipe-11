import json

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


class RouteExecutorNode(Node):
    def __init__(self):
        super().__init__("route_executor_node")

        self.declare_parameter("wall_cmd_topic", "/wall_follower/cmd_vel")
        self.declare_parameter("output_cmd_topic", "/cmd_vel")
        self.declare_parameter("forward_speed", 0.30)
        self.declare_parameter("turn_linear_speed", 0.18)
        self.declare_parameter("turn_angular_speed", 1.2)
        self.declare_parameter("turn_duration_sec", 1.2)
        self.declare_parameter("straight_duration_sec", 0.8)
        self.declare_parameter("node_cooldown_sec", 1.0)

        wall_cmd_topic = self.get_parameter("wall_cmd_topic").value
        output_cmd_topic = self.get_parameter("output_cmd_topic").value

        self.create_subscription(String, "route_plan/nodes", self.route_nodes_callback, 10)
        self.create_subscription(
            String,
            "route_plan/directions",
            self.route_directions_callback,
            10,
        )
        self.create_subscription(String, "current_node", self.current_node_callback, 10)
        self.create_subscription(Twist, wall_cmd_topic, self.wall_cmd_callback, 10)

        self.cmd_pub = self.create_publisher(Twist, output_cmd_topic, 10)
        self.override_timer = self.create_timer(0.1, self.override_timer_callback)

        self.route_nodes: list[str] = []
        self.route_directions: list[str] = []
        self.last_wall_cmd = Twist()
        self.route_index: int | None = None
        self.last_executed_node: str | None = None
        self.last_seen_node: str | None = None
        self.last_seen_time_sec = 0.0
        self.override_until_sec = 0.0
        self.override_cmd = Twist()

    def route_nodes_callback(self, msg: String) -> None:
        self.route_nodes = json.loads(msg.data)
        self.route_index = None
        self.last_executed_node = None

    def route_directions_callback(self, msg: String) -> None:
        self.route_directions = json.loads(msg.data)

    def wall_cmd_callback(self, msg: Twist) -> None:
        self.last_wall_cmd = msg
        if not self._is_override_active():
            self.cmd_pub.publish(msg)

    def current_node_callback(self, msg: String) -> None:
        if not self.route_nodes or not self.route_directions:
            return

        current_node = msg.data
        now_sec = self.get_clock().now().nanoseconds * 1e-9
        cooldown = float(self.get_parameter("node_cooldown_sec").value)

        if current_node == self.last_seen_node and now_sec - self.last_seen_time_sec < cooldown:
            return

        self.last_seen_node = current_node
        self.last_seen_time_sec = now_sec

        if current_node not in self.route_nodes:
            return

        if self.route_index is None:
            self.route_index = self.route_nodes.index(current_node)
        elif (
            self.route_index + 1 < len(self.route_nodes)
            and self.route_nodes[self.route_index + 1] == current_node
        ):
            self.route_index += 1
        elif self.route_nodes[self.route_index] != current_node:
            self.route_index = self.route_nodes.index(current_node)

        if self.route_index >= len(self.route_directions):
            return

        if self.last_executed_node == current_node:
            return

        self.last_executed_node = current_node
        self._start_override_for_direction(self.route_directions[self.route_index])

    def override_timer_callback(self) -> None:
        if self._is_override_active():
            self.cmd_pub.publish(self.override_cmd)

    def _start_override_for_direction(self, direction: str) -> None:
        self.override_cmd = Twist()

        if direction == "g":
            self.override_cmd.linear.x = float(
                self.get_parameter("turn_linear_speed").value
            )
            self.override_cmd.angular.z = float(
                self.get_parameter("turn_angular_speed").value
            )
            duration = float(self.get_parameter("turn_duration_sec").value)
        elif direction == "d":
            self.override_cmd.linear.x = float(
                self.get_parameter("turn_linear_speed").value
            )
            self.override_cmd.angular.z = -float(
                self.get_parameter("turn_angular_speed").value
            )
            duration = float(self.get_parameter("turn_duration_sec").value)
        else:
            self.override_cmd.linear.x = float(self.get_parameter("forward_speed").value)
            self.override_cmd.angular.z = 0.0
            duration = float(self.get_parameter("straight_duration_sec").value)

        now_sec = self.get_clock().now().nanoseconds * 1e-9
        self.override_until_sec = now_sec + duration

    def _is_override_active(self) -> bool:
        now_sec = self.get_clock().now().nanoseconds * 1e-9
        return now_sec < self.override_until_sec


def main(args=None):
    rclpy.init(args=args)
    node = RouteExecutorNode()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
