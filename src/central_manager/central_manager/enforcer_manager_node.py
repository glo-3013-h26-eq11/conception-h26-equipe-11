from central_manager.enforcers.base_enforcer import Enforcer
from central_manager.state_machine import StateMachineRover
from web_interface.system_health_node import HealthPingingNode
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Float32, Bool
from typing import List
import rclpy
import json
import threading
from yasmin import Blackboard


class EnforcerManagerNode(HealthPingingNode):
    def __init__(self):
        super().__init__("enforcer_manager_node", "central_manager")

        # Velocity I/O
        self.create_subscription(Twist, "/cmd_vel", self.cmd_callback, 10)
        self.pub_cmd_vel_safe = self.create_publisher(Twist, "/cmd_vel_safe", 10)

        # Publishers shared across states
        self.load_over_publisher = self.create_publisher(String, "load_over", 10)
        self.deposit_over_publisher = self.create_publisher(String, "deposit_over", 10)
        self.turn_over_publisher = self.create_publisher(String, "turn_over", 10)

        # All topic subscriptions live here — one place, no duplication
        self.create_subscription(String, "current_node", self._current_node_callback, 10)
        self.create_subscription(Float32, "distance_to_car", self._distance_to_car_callback, 10)
        self.create_subscription(Bool, "rover/start", self._rover_start_callback, 10)
        self.create_subscription(String, "turn_over", self._turn_over_callback, 10)
        self.create_subscription(String, "load_over", self._load_over_callback, 10)
        self.create_subscription(String, "deposit_over", self._deposit_over_callback, 10)
        self.create_subscription(Bool, "/proximity_sensor/merchandise", self._merchandise_callback, 10)

        # Shared blackboard passed to all states
        self.blackboard = Blackboard()
        self.blackboard["enforcers"] = []
        self.blackboard["active_state"] = None
        self.blackboard["current_node_id"] = None
        self.blackboard["current_node_distance"] = None
        self.blackboard["rover_running"] = False
        self.blackboard["route_mode"] = "load"  # load / deposit
        self.blackboard["turn_over"] = False
        self.blackboard["load_over"] = False
        self.blackboard["deposit_over"] = False
        self.blackboard["merchandise_loaded"] = False

        self.sm = StateMachineRover(self)

        self._sm_thread = threading.Thread(target=self._run_sm, daemon=True)
        self._sm_thread.start()

    # ---------- Subscription callbacks (single source of truth) ----------

    def _current_node_callback(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
            self.blackboard["current_node_id"] = str(data.get("id"))
            self.blackboard["current_node_distance"] = float(data.get("distance", 0.0))

            # Forward distance to the stop sign enforcer if one is active
            for enforcer in self._get_enforcers():
                if hasattr(enforcer, "update_distance"):
                    enforcer.update_distance(self.blackboard["current_node_distance"])
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            self.get_logger().error(f"current_node parse error: {e}")

    def _distance_to_car_callback(self, msg: Float32) -> None:
        for enforcer in self._get_enforcers():
            if hasattr(enforcer, "update_distance") and enforcer.__class__.__name__ == "CarFollowEnforcer":
                enforcer.update_distance(msg.data)

    def _rover_start_callback(self, msg: Bool) -> None:
        self.blackboard["rover_running"] = msg.data

    def _turn_over_callback(self, msg: String) -> None:
        self.blackboard["turn_over"] = True

    def _load_over_callback(self, msg: String) -> None:
        self.blackboard["load_over"] = True
        self.blackboard["merchandise_loaded"] = True

    def _deposit_over_callback(self, msg: String) -> None:
        self.blackboard["deposit_over"] = True
        self.blackboard["merchandise_loaded"] = False

    def _merchandise_callback(self, msg: Bool) -> None:
        for enforcer in self._get_enforcers():
            if hasattr(enforcer, "merchandise_callback"):
                enforcer.merchandise_callback(msg)
                print("Merchandise has been callbacked")

    # ---------- Enforcer pipeline ----------

    def _get_enforcers(self) -> List[Enforcer]:
        return self.blackboard["enforcers"]

    def cmd_callback(self, cmd: Twist) -> None:
        for enforcer in self._get_enforcers():
            cmd = enforcer.enforce_cmd(cmd)

        for enforcer in self._get_enforcers():
            enforcer.update_with_real_speed(cmd)

        self.pub_cmd_vel_safe.publish(cmd)

    def _run_sm(self):
        self.get_logger().info("Starting the state machine...")
        self.sm.run(self.blackboard)


def main(args=None):
    rclpy.init(args=args)
    enforcer_manager_node = EnforcerManagerNode()
    rclpy.spin(enforcer_manager_node)
    enforcer_manager_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()