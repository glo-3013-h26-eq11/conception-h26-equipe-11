from central_manager.base_enforcer import Enforcer
from central_manager.merchandise_enforcer import MerchandiseEnforcer
from central_manager.left_turn_enforcer import LeftTurnEnforcer
from central_manager.stopSignEnforcer import StopSignEnforcer
from central_manager.car_follow_enforcer import CarFollowEnforcer
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
from typing import List, Optional
import json
import rclpy


class EnforcerManagerNode(Node):
    def __init__(self):
        super().__init__("enforcer_manager_node")

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

        self.sub_route_nodes = self.create_subscription(
            String, "route_plan/nodes", self.route_nodes_callback, 10
        )

        self.pub_cmd_vel_safe = self.create_publisher(Twist, "/cmd_vel_safe", 10)

        self.pub_invalid_destination = self.create_publisher(
            Bool, "/merchandise_destination_invalid", 10
        )

        self.enforcers: List[Enforcer] = [
            LeftTurnEnforcer(),
            MerchandiseEnforcer(),
            StopSignEnforcer(),
            CarFollowEnforcer(),
        ]
        self.stop_sign_enforcer._logger = self.get_logger()
        self.car_follow_enforcer._logger = self.get_logger()

    @property
    def left_turn_enforcer(self) -> LeftTurnEnforcer:
        return self.enforcers[0]

    @property
    def merchandise_enforcer(self) -> MerchandiseEnforcer:
        return self.enforcers[1]

    @property
    def stop_sign_enforcer(self) -> StopSignEnforcer:
        return self.enforcers[2]

    @property
    def car_follow_enforcer(self) -> CarFollowEnforcer:
        return self.enforcers[3]

    def load_callback(self, load_msg: Bool) -> None:
        self.merchandise_enforcer.load_detected = load_msg.data

        loaded_merchandise: bool = self.merchandise_enforcer.load_detected
        destination_node: str = self.merchandise_enforcer.destination
        if (
            loaded_merchandise
            and destination_node
            and destination_node.startswith("ZC")
        ):
            invalid_dest_msg = Bool()
            invalid_dest_msg.data = True
            self.pub_invalid_destination.publish(invalid_dest_msg)

    def cmd_callback(self, cmd: Twist) -> None:
        for enforcer in self.enforcers:
            cmd = enforcer.enforce_cmd(cmd)

        self.left_turn_enforcer.update_real_speed(cmd)

        self.pub_cmd_vel_safe.publish(cmd)

    def route_nodes_callback(self, msg: String) -> None:
        nodes: List[str] = json.loads(msg.data)
        destination_node: str = nodes[-1]
        self.merchandise_enforcer.destination = destination_node

    def aruco_callback(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
            markers_5x5 = payload.get("markers_5x5", [])
            markers_4x4 = payload.get("markers_4x4", [])

            closest_stop_dist: Optional[float] = None
            for marker in markers_5x5:
                d = float(marker.get("depth", 9999))
                angle = float(marker.get("angle_x_deg", 0))
                z_fwd = float(marker.get("z_forward", 0))
                if d <= 1.0 and angle <= 35.0 and z_fwd >= 0.15:
                    if closest_stop_dist is None or d < closest_stop_dist:
                        closest_stop_dist = d

            self.stop_sign_enforcer.update_distance(closest_stop_dist)

            closest_vehicle_dist: Optional[float] = None
            for marker in markers_4x4:
                d = float(marker.get("depth", 9999))
                angle = float(marker.get("angle_x_deg", 0))
                if angle <= 90.0:
                    if closest_vehicle_dist is None or d < closest_vehicle_dist:
                        closest_vehicle_dist = d
            self.car_follow_enforcer.update_distance(closest_vehicle_dist)
        except Exception:
            pass


def main(args=None):
    rclpy.init(args=args)

    enforcer_manager_node = EnforcerManagerNode()

    rclpy.spin(enforcer_manager_node)

    enforcer_manager_node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
