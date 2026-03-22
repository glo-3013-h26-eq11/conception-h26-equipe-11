from central_manager.enforcers.base_enforcer import Enforcer
from central_manager.state_machine import StateMachineRover
from central_manager.central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from rclpy.node import Node
from web_interface.web_interface.system_health_node import HealthPingingNode
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from typing import List
from std_msgs.msg import String, Bool
from typing import List
import json
import rclpy
import threading
from yasmin import Blackboard


class EnforcerManagerNode(HealthPingingNode):
    def __init__(self):
        super().__init__("enforcer_manager_node", "central_manager")

        self.sub_load_detection = self.create_subscription(
            Bool, "is_there_merchandise", self.load_callback, 10
        )

        self.sub_aruco = self.create_subscription(
            String,
            "aruco_detections",
            self.aruco_callback,
            10,
        )

        self.sub_cmd_vel = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_callback, 10
        )

        self.pub_cmd_vel_safe = self.create_publisher(Twist, "/cmd_vel_safe", 10)

        self.pub_invalid_destination = self.create_publisher(
            Bool, "/merchandise_destination_invalid", 10
        )

        self.pub_dangerous_distance_car_follower = self.create_publisher(
            Bool, "/car_follower/dangerous_distance", 10
        )

        self.blackboard = Blackboard()

        self.blackboard["enforcers"] = []

        self.sm = StateMachineRover(self)

        self._sm_thread = threading.Thread(target=self._run_sm, daemon=True)
        self._sm_thread.start()

    def _get_enforcers(self) -> List[Enforcer]:
        return self.blackboard["enforcers"]

    def _run_sm(self):
        self.get_logger().info("Starting the state machine...")

        self.sm.run(self.blackboard)

    def cmd_callback(self, cmd: Twist) -> None:
        for enforcer in self._get_enforcers():
            cmd = enforcer.enforce_cmd(cmd)

        for enforcer in self._get_enforcers():
            enforcer.update_with_real_speed(cmd)

        self.pub_cmd_vel_safe.publish(cmd)

    def route_nodes_callback(self, msg: String) -> None:
        nodes: List[str] = json.loads(msg.data)
        destination_node: str = nodes[-1]
        self.merchandise_enforcer.destination = destination_node
            
        
    def publish_dangerous_distance(self):
        dangerous_distance = Bool()
        dangerous_distance.data = True
        self.pub_dangerous_distance_car_follower.publish(dangerous_distance)


def main(args=None):
    rclpy.init(args=args)

    enforcer_manager_node = EnforcerManagerNode()

    rclpy.spin(enforcer_manager_node)

    enforcer_manager_node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
