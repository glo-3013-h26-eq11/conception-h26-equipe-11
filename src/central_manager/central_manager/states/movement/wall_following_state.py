from typing import Optional
import json
from std_msgs.msg import String, Float32, Bool
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)
from navigation_interfaces.srv import GetIsIntersectionValidToStop
from functools import partial
from central_manager.state_base import RoverState


class WallFollowingState(RoverState):
    def __init__(self, node):
        self.node = node

        node.create_subscription(
            String, "current_node", self.at_intersection_callback, 10
        )
        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )
        node.create_subscription(Bool, "stop_over", self.stop_over, 10)
        node.create_subscription(
            Float32, "/wall_follower/alpha", self.alpha_callback, 10
        )
        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.stop_over_publisher = node.create_publisher(Bool, "stop_over", 10)
        self.car_follower_enforcer: CarFollowEnforcer = None
        self.stop_sign_enforcer: StopSignEnforcer = None
        self.latest_alpha = 0.0
        self.outcome = None
        self.seen_tag = None
        self.previous_tag = None
        self.blackboard = None
        self.client = self.node.create_client(
            GetIsIntersectionValidToStop, "get_is_intersection_valid_to_stop"
        )

    def alpha_callback(self, msg: Float32):
        self.latest_alpha = msg.data

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def at_intersection_callback(self, msg: String):
        data = json.loads(msg.data)

        distance = float(data.get("distance"))
        angle = float(data.get("angle"))
        self.seen_tag = data.get("tag")

        self.get_is_the_intersection_valid_to_stop(self.seen_tag)

        if self.previous_tag is not None and self.seen_tag == self.previous_tag:
            return

        if self.stop_sign_enforcer:
            self.stop_sign_enforcer.update_distance(distance)
            self.stop_sign_enforcer.update_relative_angle(angle)

    def get_is_the_intersection_valid_to_stop(self, aruco_tag: int) -> bool:
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.node.get_logger().error("get_is_intersection_valid_to_stop")
            raise RuntimeError("Service 'get_is_intersection_valid_to_stop")

        request = GetIsIntersectionValidToStop.Request()
        request.aruco_tag = aruco_tag
        future = self.client.call_async(request)
        future.add_done_callback(
            partial(self.handle_get_is_the_intersection_valid_to_stop, aruco_tag)
        )

    def handle_get_is_the_intersection_valid_to_stop(self, aruco_tag, future):
        result = future.result()

        if result is not None and result.is_valid is False:
            if self.previous_tag != aruco_tag:
                self.node.get_logger().info(
                    f"Skipping stopping at tag : {aruco_tag}"
                )
                self.previous_tag = aruco_tag

    def stop_over(self, msg: Bool):
        self.node.get_logger().info("STOPPED : SAYS WALL FOLLOWER")
        if self.blackboard is not None:
            self.blackboard["arrival_alpha_rad"] = self.latest_alpha
        self.outcome = "current_node"

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def on_enter(self, blackboard):
        self.blackboard = blackboard
        self.outcome = None
        self.previous_tag = blackboard[BLACKBOARD_PREVIOUS_STOP_TAG]
        self.node.get_logger().info("WALL_FOLLOWING_STATE state")
        self.car_follower_enforcer = CarFollowEnforcer()
        self.stop_sign_enforcer = StopSignEnforcer(
            self.stop_over_publisher, logger=self.node.get_logger()
        )
        blackboard[BLACKBOARD_ENFORCERS] = [
            self.stop_sign_enforcer,
            self.car_follower_enforcer,
        ]

    def step(self, blackboard) -> Optional[str]:
        if self.outcome is None:
            return None

        blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = self.seen_tag
        return self.outcome
