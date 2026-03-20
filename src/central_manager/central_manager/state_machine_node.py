#!/usr/bin/env python3
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from yasmin import StateMachine
from threading import Thread


from central_manager.states.initial_state import InitialState
from central_manager.states.wall_following_state import WallFollowingState
from central_manager.states.at_intersection_state import AtIntersectionState
from central_manager.states.turning_left_state import TurningLeftState
from central_manager.states.turning_forward_state import TurningForwardState
from central_manager.states.at_pickup_zone_state import AtPickupZoneState
from central_manager.states.waiting_pickup_merchandise_state import WaitingPickupMerchandiseState
from central_manager.states.at_delivery_zone_state import AtDeliveryZoneState
from central_manager.states.waiting_delivery_merchandise_state import WaitingDeliveryMerchandiseState

class StateMachineNode(Node):
    def __init__(self):
        super().__init__("state_machine_node")

        self.blackboard = {}
        self._init_blackboard()
        self.blackboard["node"] = self

        self.active_enforcers_pub = self.create_publisher(
            String, "state_machine/active_enforcers", 10
        )

        self.create_subscription(
            String, "aruco_detections", self.aruco_callback, 10
        )

        self.create_subscription(
            String, "route_plan/directions", self.route_directions_callback, 10
        )

        self.create_subscription(
            Bool, "is_there_merchandise", self.merchandise_callback, 10
        )

        self.create_subscription(
            Bool, "turn_complete", self.turn_complete_callback, 10
        )
        
        self.create_subscription(
            Bool, "zone_stop_complete", self.zone_stop_complete_callback, 10
        )

        self.states = self.create_states()
        self.sm = self.create_state_machine()
        
        self.fsm_thread = Thread(target=self.run_state_machine, daemon=True)
        self.fsm_thread.start()
        
    def _init_blackboard(self):
        self.blackboard["system_ready_flag"] = True

        self.blackboard["intersection_detected_flag"] = False
        self.blackboard["pickup_zone_detected_flag"] = False
        self.blackboard["delivery_zone_detected_flag"] = False
        self.blackboard["merchandise_detected_flag"] = False
        self.blackboard["turn_complete_flag"] = False
        self.blackboard["zone_stop_complete_flag"] = False

        self.blackboard["route_directions"] = []
        self.blackboard["next_direction"] = None
        self.blackboard["active_enforcers"] = []

    def create_states(self):
        return {
            "INITIAL": InitialState(),
            "WALL_FOLLOWING": WallFollowingState(),
            "AT_INTERSECTION": AtIntersectionState(),
            "TURNING_LEFT": TurningLeftState(),
            "TURNING_FORWARD": TurningForwardState(),
            "AT_PICKUP_ZONE": AtPickupZoneState(),
            "WAITING_PICKUP_MERCHANDISE": WaitingPickupMerchandiseState(),
            "AT_DELIVERY_ZONE": AtDeliveryZoneState(),
            "WAITING_DELIVERY_MERCHANDISE": WaitingDeliveryMerchandiseState(),
        }
        
    def create_state_machine(self):
        sm = StateMachine(outcomes=["mission_complete", "error"])

        sm.add_state(
            "INITIAL",
            self.states["INITIAL"],
            transitions={
                "system_ready": "WALL_FOLLOWING",
                "continue": "INITIAL",
                
            },
        )

        sm.add_state(
            "WALL_FOLLOWING",
            self.states["WALL_FOLLOWING"],
            transitions={
                "intersection_detected": "AT_INTERSECTION",
                "pickup_zone_detected": "AT_PICKUP_ZONE",
                "delivery_zone_detected": "AT_DELIVERY_ZONE",
                "continue": "WALL_FOLLOWING",
            },
        )

        sm.add_state(
            "AT_INTERSECTION",
            self.states["AT_INTERSECTION"],
            transitions={
                "turn_left": "TURNING_LEFT",
                "turn_forward": "TURNING_FORWARD",
                "turn_right": "WALL_FOLLOWING",
                "continue": "AT_INTERSECTION",
            },
        )

        sm.add_state(
            "TURNING_LEFT",
            self.states["TURNING_LEFT"],
            transitions={
                "turn_complete": "WALL_FOLLOWING",
                "continue": "TURNING_LEFT",
            },
        )

        sm.add_state(
            "TURNING_FORWARD",
            self.states["TURNING_FORWARD"],
            transitions={
                "turn_complete": "WALL_FOLLOWING",
                "continue": "TURNING_FORWARD",
            },
        )

        sm.add_state(
            "AT_PICKUP_ZONE",
            self.states["AT_PICKUP_ZONE"],
            transitions={
                "stopped": "WAITING_PICKUP_MERCHANDISE",
                "continue": "AT_PICKUP_ZONE",
            },
        )

        sm.add_state(
            "WAITING_PICKUP_MERCHANDISE",
            self.states["WAITING_PICKUP_MERCHANDISE"],
            transitions={
                "merchandise_loaded": "WALL_FOLLOWING",
                "continue": "WAITING_PICKUP_MERCHANDISE",
            },
        )

        sm.add_state(
            "AT_DELIVERY_ZONE",
            self.states["AT_DELIVERY_ZONE"],
            transitions={
                "stopped": "WAITING_DELIVERY_MERCHANDISE",
                "continue": "AT_DELIVERY_ZONE",
            },
        )

        sm.add_state(
            "WAITING_DELIVERY_MERCHANDISE",
            self.states["WAITING_DELIVERY_MERCHANDISE"],
            transitions={
                "merchandise_unloaded": "WALL_FOLLOWING",
                "continue": "WAITING_DELIVERY_MERCHANDISE",
            },
        )

        return sm
    
    def run_state_machine(self):
        try:
            outcome = self.sm(self.blackboard)
            self.get_logger().info(f"FSM finished with outcome: {outcome}")
        except Exception as e:
            self.get_logger().error(f"FSM execution error: {e}")
    
    def publish_active_enforcers(self, enforcer_names):
        msg = String()
        msg.data = json.dumps(enforcer_names)
        self.active_enforcers_pub.publish(msg)

    def aruco_callback(self, msg: String):
        try:
            payload = json.loads(msg.data)
            markers_5x5 = payload.get("markers_5x5", [])

            if len(markers_5x5) > 0:
                self.blackboard["intersection_detected_flag"] = True

        except Exception as e:
            self.get_logger().error(f"aruco_callback error: {e}")

    def route_directions_callback(self, msg: String):
        try:
            directions = json.loads(msg.data)
            self.blackboard["route_directions"] = directions

            if directions:
                self.blackboard["next_direction"] = directions[0]
            else:
                self.blackboard["next_direction"] = None

        except Exception as e:
            self.get_logger().error(f"route_directions_callback error: {e}")

    def merchandise_callback(self, msg: Bool):
        self.blackboard["merchandise_detected_flag"] = msg.data
        
    def turn_complete_callback(self, msg: Bool):
        self.blackboard["turn_complete_flag"] = msg.data
        
    def zone_stop_complete_callback(self, msg: Bool):
        self.blackboard["zone_stop_complete_flag"] = msg.data

def main(args=None):
    rclpy.init(args=args)

    node = StateMachineNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()