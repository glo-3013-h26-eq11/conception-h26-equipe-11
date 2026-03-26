import json

from yasmin import State
from std_msgs.msg import Bool, String
import rclpy
from central_manager.enforcers.immobile_enforcer import ImmobileEnforcer


class InitialState(State):
    def __init__(self, node):
        super().__init__(
            outcomes=[
                "system_ready",
            ]
        )

        self.node = node

        node.create_subscription(Bool, "rover/start", self.rover_start_callback, 10)

        node.create_subscription(
            String, "current_node", self.at_deposit_callback, 10
        )

        self.home_deposit_zone_pub = self.create_publisher(String, "home_deposit_node", 10)

        self.home_deposit_zone = None

        self.outcome = None

    def rover_start_callback(self, msg):
        if msg.data:
            self.outcome = "system_ready"

    def at_deposit_callback(self, msg):
        data = json.loads(msg.data)

        seen_tag = data.get("tag")
        
        if not seen_tag == None and self.home_deposit_zone == None:
            self.home_deposit_zone = seen_tag
            self.home_deposit_zone_pub.publish(seen_tag)


    def execute(self, blackboard):
        self.outcome = None

        self.node.get_logger().info("INITIAL state")

        blackboard["enforcers"] = [ImmobileEnforcer()]

        blackboard["previous_stop_tag"] = None
        blackboard["home_deposit_zone"] = self.home_deposit_zone

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        return self.outcome
