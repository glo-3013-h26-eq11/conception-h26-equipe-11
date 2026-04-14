from typing import Optional
from std_msgs.msg import String, Float32, Bool
from central_manager.enforcers.forward_turn_enforcer import ForwardTurnEnforcer
from central_manager.enforcers.car_follow_enforcer import CarFollowEnforcer
from central_manager.blackboard_config import BLACKBOARD_ENFORCERS
from central_manager.state_base import RoverState


class TurningForwardState(RoverState):
    def __init__(self, node):
        self.node = node

        node.create_subscription(String, "turn_over", self.turn_over_callback, 10)
        node.create_subscription(
            Float32, "distance_to_car", self.distance_to_car_callback, 10
        )
        node.create_subscription(Bool, "rover/start", self.rover_stop_callback, 10)

        self.turn_over_publisher = node.create_publisher(String, "turn_over", 10)
        self.car_follower_enforcer: CarFollowEnforcer = None
        self.outcome = None

    def turn_over_callback(self, msg: String):
        self.outcome = "turn_over"

    def distance_to_car_callback(self, msg: Float32):
        if self.car_follower_enforcer:
            self.car_follower_enforcer.update_distance(msg.data)

    def rover_stop_callback(self, msg: Bool):
        if not msg.data:
            self.outcome = "back_to_init"

    def on_enter(self, blackboard):
        self.outcome = None
        self.node.get_logger().info("TURNING_FORWARD state")

        self.car_follower_enforcer = CarFollowEnforcer()
        blackboard[BLACKBOARD_ENFORCERS] = [
            ForwardTurnEnforcer(self.turn_over_publisher),
            self.car_follower_enforcer,
        ]

    def step(self, blackboard) -> Optional[str]:
        return self.outcome
