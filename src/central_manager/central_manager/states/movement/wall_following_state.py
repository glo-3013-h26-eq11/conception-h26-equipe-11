from yasmin import State
import rclpy
from std_msgs.msg import String, Float32, Bool
import json
from central_manager.enforcers.stop_sign_enforcer import StopSignEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import (
    BLACKBOARD_ENFORCERS,
    BLACKBOARD_PREVIOUS_STOP_TAG,
)
from navigation_interfaces.srv import GetIsIntersectionValidToStop



class WallFollowingState(State):
    def __init__(self, node):
        super().__init__(outcomes=["current_node", "back_to_init"])

        self.node = node

        node.create_subscription(
            String, "current_node", self.at_intersection_callback, 10
        )

        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )

        node.create_subscription(Bool, "stop_over", self.stop_over, 10)

        self.stop_over_publisher = node.create_publisher(Bool, "stop_over", 10)

        self.car_follower_enforcer: CarFollowEnforcer = None

        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.stop_sign_enforcer: StopSignEnforcer = None

        self.outcome = None

        self.cooldown = None

        self.seen_tag = None

        self.previous_tag = None
        
        self.client = self.node.create_client(GetIsIntersectionValidToStop, "get_is_intersection_valid_to_stop")

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def at_intersection_callback(self, msg: String):
        data = json.loads(msg.data)

        distance = float(data.get("distance"))
        angle = float(data.get("angle"))

        self.seen_tag = data.get("tag")

        if self.previous_tag is not None:
            if self.seen_tag == self.previous_tag:
                return
            
        is_intersection_valid_to_stop = self.get_is_the_intersection_valid_to_stop(self.seen_tag)
        
        if not is_intersection_valid_to_stop:
            self.outcome = "current_node"

        if self.stop_sign_enforcer:
            self.stop_sign_enforcer.update_distance(distance)
            self.stop_sign_enforcer.update_relative_angle(angle)
            
    def get_is_the_intersection_valid_to_stop(self, aruco_tag:int) -> bool:
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.node.get_logger().error(
                "get_is_intersection_valid_to_stop"
            )
            raise RuntimeError("Service 'get_is_intersection_valid_to_stop")

        request = GetIsIntersectionValidToStop.Request()
        request.aruco_tag = aruco_tag
        future = self.client.call_async(request)

        while not future.done():
            rclpy.spin_once(self.node, timeout_sec=0.1)

        result = future.result()
        if result is not None:
            return result.is_valid

        self.node.get_logger().error("get_is_intersection_valid_to_stop failed")
        raise RuntimeError("get_is_intersection_valid_to_stop failed")

    def stop_over(self, msg: Bool):
        self.node.get_logger().info("STOPPED : SAYS WALL FOLLOWER")
        self.outcome = "current_node"

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def execute(self, blackboard):
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

        while self.outcome is None:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        blackboard[BLACKBOARD_PREVIOUS_STOP_TAG] = self.seen_tag

        return self.outcome
