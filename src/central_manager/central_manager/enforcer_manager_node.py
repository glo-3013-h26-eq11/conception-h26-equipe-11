from central_manager.enforcers.base_enforcer import Enforcer
from central_manager.state_machine import StateMachineRover
from web_interface.system_health_node import HealthPingingNode
from geometry_msgs.msg import Twist
from typing import List
import rclpy
import threading
from yasmin import Blackboard


class EnforcerManagerNode(HealthPingingNode):
    def __init__(self):
        super().__init__("enforcer_manager_node", "central_manager")


        self.sub_cmd_vel = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_callback, 10
        )

        self.pub_cmd_vel_safe = self.create_publisher(Twist, "/cmd_vel_safe", 10)


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
            
        print(cmd)

        self.pub_cmd_vel_safe.publish(cmd)


def main(args=None):
    rclpy.init(args=args)

    enforcer_manager_node = EnforcerManagerNode()

    rclpy.spin(enforcer_manager_node)

    enforcer_manager_node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
