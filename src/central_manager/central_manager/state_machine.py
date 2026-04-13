from typing import Optional
from rclpy.node import Node

from central_manager.states.initial.initial_state import InitialState
from central_manager.states.to_load.at_intersection_to_load_state import (
    AtIntersectionToLoadState,
)
from central_manager.states.movement.turning_left_state import TurningLeftState
from central_manager.states.movement.turning_forward_state import TurningForwardState
from central_manager.states.movement.wall_following_state import WallFollowingState
from central_manager.states.to_load.at_load_zone_to_load_state import AtLoadZoneToLoad
from central_manager.states.to_deposit.at_intersection_to_deposit_state import (
    AtIntersectionToDepositState,
)
from central_manager.states.to_deposit.at_deposit_zone_to_deposit_state import (
    AtDepositZoneToDeposit,
)


class StateMachineRover:
    def __init__(self, node: Node):
        self.node = node
        self.states = self.create_states(node)
        self.transitions = self.create_transitions()
        self.current_state_name = None
        self.current_state = None

    def start(self, blackboard: dict) -> None:
        self._transition_to("INITIAL", blackboard)

    def step(self, blackboard: dict) -> Optional[str]:
        if self.current_state is None:
            self.start(blackboard)
            return self.current_state_name

        outcome = self.current_state.step(blackboard)
        if outcome is None:
            return None

        next_state_name = self.transitions[self.current_state_name].get(outcome)
        if next_state_name is None:
            self.node.get_logger().error(
                f"Unknown transition from {self.current_state_name} on {outcome}"
            )
            raise RuntimeError(
                f"Invalid transition: {self.current_state_name} -> {outcome}"
            )

        self._transition_to(next_state_name, blackboard)
        return next_state_name

    def _transition_to(self, state_name: str, blackboard: dict) -> None:
        self.current_state_name = state_name
        self.current_state = self.states[state_name]
        self.node.get_logger().info(f"Entering state: {state_name}")
        self.current_state.on_enter(blackboard)

    def create_states(self, node):
        return {
            "INITIAL": InitialState(node),
            "WALL_FOLLOWING_POSITIONING": WallFollowingState(node),
            "AT_INTERSECTION_TO_LOAD": AtIntersectionToLoadState(node),
            "TURNING_LEFT_TO_LOAD": TurningLeftState(node),
            "TURNING_FORWARD_TO_LOAD": TurningForwardState(node),
            "WALL_FOLLOWING_TO_LOAD": WallFollowingState(node),
            "AT_LOAD_ZONE_TO_LOAD": AtLoadZoneToLoad(node),
            "AT_INTERSECTION_TO_DEPOSIT": AtIntersectionToDepositState(node),
            "TURNING_LEFT_TO_DEPOSIT": TurningLeftState(node),
            "TURNING_FORWARD_TO_DEPOSIT": TurningForwardState(node),
            "WALL_FOLLOWING_TO_DEPOSIT": WallFollowingState(node),
            "AT_DEPOSIT_ZONE_TO_DEPOSIT": AtDepositZoneToDeposit(node),
        }

    def create_transitions(self):
        return {
            "INITIAL": {
                "system_ready": "WALL_FOLLOWING_POSITIONING",
                "back_to_init": "INITIAL",
            },
            "WALL_FOLLOWING_POSITIONING": {
                "current_node": "AT_INTERSECTION_TO_LOAD",
                "back_to_init": "INITIAL",
            },
            "AT_INTERSECTION_TO_LOAD": {
                "left_turn": "TURNING_LEFT_TO_LOAD",
                "forward_turn": "TURNING_FORWARD_TO_LOAD",
                "right_turn": "WALL_FOLLOWING_TO_LOAD",
                "wait_load_zone": "AT_LOAD_ZONE_TO_LOAD",
                "back_to_init": "INITIAL",
            },
            "TURNING_LEFT_TO_LOAD": {
                "turn_over": "WALL_FOLLOWING_TO_LOAD",
                "back_to_init": "INITIAL",
            },
            "TURNING_FORWARD_TO_LOAD": {
                "turn_over": "WALL_FOLLOWING_TO_LOAD",
                "back_to_init": "INITIAL",
            },
            "WALL_FOLLOWING_TO_LOAD": {
                "current_node": "AT_INTERSECTION_TO_LOAD",
                "back_to_init": "INITIAL",
            },
            "AT_LOAD_ZONE_TO_LOAD": {
                "load_over": "AT_INTERSECTION_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
            "AT_INTERSECTION_TO_DEPOSIT": {
                "left_turn": "TURNING_LEFT_TO_DEPOSIT",
                "forward_turn": "TURNING_FORWARD_TO_DEPOSIT",
                "right_turn": "WALL_FOLLOWING_TO_DEPOSIT",
                "wait_deposit_zone": "AT_DEPOSIT_ZONE_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
            "TURNING_LEFT_TO_DEPOSIT": {
                "turn_over": "WALL_FOLLOWING_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
            "TURNING_FORWARD_TO_DEPOSIT": {
                "turn_over": "WALL_FOLLOWING_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
            "WALL_FOLLOWING_TO_DEPOSIT": {
                "current_node": "AT_INTERSECTION_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
            "AT_DEPOSIT_ZONE_TO_DEPOSIT": {
                "deposit_over": "AT_INTERSECTION_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        }
