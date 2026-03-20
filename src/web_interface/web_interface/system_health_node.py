import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
from datetime import datetime
from enum import Enum

HEARTBEAT_TIMEOUT = 3.0


class NodeStatus(Enum):
    LOADING = "LOADING"
    ACTIVE = "ACTIVE"
    CRASHED = "CRASHED"


class NodeInfo:
    def __init__(self, name, system):
        self.name = name
        self.system = system
        self.status = NodeStatus.LOADING
        self.last_seen = None

    def update(self, status=NodeStatus.ACTIVE):
        self.status = status
        self.last_seen = datetime.now().timestamp()

    def check_timeout(self, now):
        if self.last_seen is None:
            return

        if (now - self.last_seen) > HEARTBEAT_TIMEOUT:
            self.status = NodeStatus.CRASHED


class HealthMonitorNode(Node):
    def __init__(self):
        super().__init__("health_monitor")

        self._nodes: dict[str, NodeInfo] = {}

        self.heartbeat_sub = self.create_subscription(
            String, "/health/heartbeat", self._on_heartbeat, 10
        )

        self._status_pub = self.create_publisher(String, "/health_status", 10)

        self.create_timer(1.0, self._tick)

        self.get_logger().info("Health monitor started")

    def _on_heartbeat(self, msg: String):
        data = json.loads(msg.data)

        name = data["name"]
        system = data["system"]

        if "status" in data:
            status = NodeStatus(data["status"])
        else:
            status = NodeStatus.ACTIVE

        if name not in self._nodes:
            self._nodes[name] = NodeInfo(name, system)
            self.get_logger().info(f"New node detected : [{system}] {name}")

        self._nodes[name].update(status=status)

    def _tick(self):
        now = datetime.now().timestamp()

        for node in self._nodes.values():
            node.check_timeout(now)

        summary: dict[str, dict[str, str]] = {}
        for node in self._nodes.values():
            summary.setdefault(node.system, {})[node.name] = node.status.value

        self._status_pub.publish(String(data=json.dumps(summary)))


def main():
    rclpy.init()
    node = HealthMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        node.get_logger().fatal(e)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
