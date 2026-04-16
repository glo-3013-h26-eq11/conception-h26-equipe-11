from central_manager.enforcers.base_enforcer import Enforcer
from central_manager.state_machine import StateMachineRover
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)
from web_interface.system_health_node import HealthPingingNode
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from typing import List
import rclpy


class EnforcerManagerNode(HealthPingingNode):
    def __init__(self, state_machine=None):
        super().__init__("enforcer_manager_node", "central_manager")

        self.sub_cmd_vel_from_aruco_callback = self.create_subscription(
            String, "current_node", self.camera_callback, 10
        )

        self.sub_cmd_vel = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_callback, 10
        )

        self.pub_cmd_vel_safe = self.create_publisher(Twist, "/cmd_vel_safe", 10)

        self.blackboard = {}
        self.blackboard[BLACKBOARD_ENFORCERS] = []
        self.blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = None

        self.sm = state_machine or StateMachineRover(self)
        self.sm.start(self.blackboard)
        self.create_timer(0.1, self._state_machine_tick)

        self.previous_twist = Twist()

    def _get_enforcers(self) -> List[Enforcer]:
        self.blackboard[BLACKBOARD_ENFORCERS].sort(
            key=lambda enforcer: enforcer.priority
        )
        return self.blackboard[BLACKBOARD_ENFORCERS]

    def _state_machine_tick(self) -> None:
        try:
            outcome = self.sm.step(self.blackboard)
            if outcome is not None:
                self.get_logger().info(f"Transitioned to state: {outcome}")
        except Exception as exc:
            self.get_logger().error(f"State machine error: {exc}")

    def camera_callback(self, msg: String):
        self.cmd_callback(self.previous_twist)

    def cmd_callback(self, cmd: Twist) -> None:
        self.previous_twist = cmd

        for enforcer in self._get_enforcers():
            cmd = enforcer.enforce_cmd(cmd)

        for enforcer in self._get_enforcers():
            enforcer.update_with_real_speed(cmd)

        self.pub_cmd_vel_safe.publish(cmd)


def main(args=None):
    rclpy.init(args=args)

    enforcer_manager_node = EnforcerManagerNode()

    try:
        rclpy.spin(enforcer_manager_node)
    finally:
        enforcer_manager_node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
