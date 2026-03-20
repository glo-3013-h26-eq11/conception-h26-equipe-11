#!/usr/bin/env python3
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

from central_manager.states.wall_following_state import WallFollowingState

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

        self.states = self.create_states()
        self.sm = self.create_state_machine()
        
    def _init_blackboard(self):
        self.blackboard["intersection_detected_flag"] = False
        self.blackboard["loading_zone_detected_flag"] = False
        self.blackboard["merchandise_detected_flag"] = False
        self.blackboard["turn_complete_flag"] = False

        self.blackboard["route_directions"] = []
        self.blackboard["next_direction"] = None

        self.blackboard["active_enforcers"] = []

    def create_states(self):
        return {
            "WALL_FOLLOWING": WallFollowingState(),
            "AT_INTERSECTION": AtIntersectionState(),
        }
        
    def create_state_machine(self):
        sm = StateMachine(outcomes=["mission_complete", "error"])

        sm.add_state(
            "WALL_FOLLOWING",
            self.states["WALL_FOLLOWING"],
            transitions={
                "intersection_detected": "AT_INTERSECTION",
                "loading_zone_detected": "AT_LOADING_ZONE",
                "continue": "WALL_FOLLOWING",
            },
        )

        sm.add_state(
            "AT_INTERSECTION",
            self.states["AT_INTERSECTION"],
            transitions={
                "turn_left": "TURNING_LEFT",
                "turn_forward": "TURNING_FORWARD",
                "turn_right": "TURNING_RIGHT",
                "continue": "AT_INTERSECTION",
            },
        )
        
        return sm
    
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