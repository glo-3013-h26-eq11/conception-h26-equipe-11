from central_manager.base_enforcer import Enforcer
from central_manager.merchandise_enforcer import MerchandiseEnforcer
from central_manager.stopSignEnforcer import StopSignEnforcer
from central_manager.car_follow_enforcer import CarFollowEnforcer
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
from typing import List
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

        self.enforcers: List[Enforcer] = [MerchandiseEnforcer(), StopSignEnforcer(), CarFollowEnforcer()]

        self._seen_aruco_ids: set = set()

    @property
    def merchandise_enforcer(self) -> MerchandiseEnforcer:
        return self.enforcers[0]

    @property
    def stop_sign_enforcer(self) -> StopSignEnforcer:
        return self.enforcers[1]
    
    @property
    def car_follow_enforcer(self) -> CarFollowEnforcer:
        return self.enforcers[2]

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

            close_ids_5x5 = {
                marker.get("id")
                for marker in markers_5x5
                if float(marker.get("depth", 9999)) <= 0.61
                and float(marker.get("angle_x_deg", 0)) <= 35.0
                and float(marker.get("z_forward", 0)) >= 0.15
            }
            
            close_ids_4x4 = {
                marker.get("id")
                for marker in markers_4x4
                if float(marker.get("depth", 9999)) <= 0.61
                and float(marker.get("angle_x_deg", 0)) <= 35.0
                and float(marker.get("z_forward", 0)) >= 0.15
            }

            for marker_id in close_ids_5x5:
                if marker_id not in self._seen_aruco_ids:
                    self._seen_aruco_ids.add(marker_id)
                    self.stop_sign_enforcer.stop_detected = True
                    break
            
            for marker in markers_4x4:
                if (
                    float(marker.get("depth", 9999)) <= 0.61
                    and float(marker.get("angle_x_deg", 0)) <= 35.0
                    and float(marker.get("z_forward", 0)) >= 0.15
                ):
                    self.car_follow_enforcer.follow_distance = float(marker.get("depth", 9999))
                    break
            else:
                self.car_follow_enforcer.follow_distance = None
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
