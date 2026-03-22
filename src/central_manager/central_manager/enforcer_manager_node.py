from central_manager.enforcers.base_enforcer import Enforcer
from central_manager.state_machine import StateMachineRover
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from typing import List
import rclpy


class EnforcerManagerNode(Node):
    def __init__(self):
        super().__init__("enforcer_manager_node")

        self.sub_cmd_vel = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_callback, 10
        )

        self.pub_cmd_vel_safe = self.create_publisher(Twist, "cmd_vel_safe", 10)

        self.pub_dangerous_distance_car_follower = self.create_publisher(
            Bool, "/car_follower/dangerous_distance", 10
        )

        self.blackboard = {}

        self.blackboard["enforcers"] = []

        self.sm = StateMachineRover(self)

        self.start_timer = self.create_timer(0.1, self._start_sm_once)

    def _get_enforcers(self) -> List[Enforcer]:
        return self.blackboard["enforcers"]

    def _start_sm_once(self):
        self.start_timer.cancel()

        self.get_logger().info("Starting the state machine...")

        self.sm.run(self.blackboard)

    def cmd_callback(self, cmd: Twist) -> None:
        for enforcer in self._get_enforcers():
            cmd = enforcer.enforce_cmd(cmd)

        self.pub_cmd_vel_safe.publish(cmd)

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
