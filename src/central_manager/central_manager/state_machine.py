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
from central_manager.states_enum import State
from central_manager.transitions_enum import Transition


class StateMachineRover:
    def __init__(self, node: Node):
        self.node = node
        self.states = self.create_states(node)
        self.transitions = self.create_transitions()
        self.current_state_name = None
        self.current_state = None

    def start(self, blackboard: dict) -> None:
        self._transition_to(State.INITIAL.value, blackboard)

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
            State.INITIAL.value: InitialState(node),
            State.WALL_FOLLOWING_POSITIONNING.value: WallFollowingState(node),
            State.AT_INTERSECTION_TO_LOAD.value: AtIntersectionToLoadState(node),
            State.TURNING_LEFT_TO_LOAD.value: TurningLeftState(node),
            State.TURNING_FORWARD_TO_LOAD.value: TurningForwardState(node),
            State.WALL_FOLLOWING_TO_LOAD.value: WallFollowingState(node),
            State.AT_LOAD_ZONE_TO_LOAD.value: AtLoadZoneToLoad(node),
            State.AT_INTERSECTION_TO_DEPOSIT.value: AtIntersectionToDepositState(node),
            State.TURNING_LEFT_TO_DEPOSIT.value: TurningLeftState(node),
            State.TURNING_FORWARD_TO_DEPOSIT.value: TurningForwardState(node),
            State.WALL_FOLLOWING_TO_DEPOSIT.value: WallFollowingState(node),
            State.AT_DEPOSIT_ZONE_TO_DEPOSIT.value: AtDepositZoneToDeposit(node),
        }

    def create_transitions(self):
        return {
            State.INITIAL.value: {
                Transition.SYSTEM_READY.value: State.WALL_FOLLOWING_POSITIONNING.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.WALL_FOLLOWING_POSITIONNING.value: {
                Transition.CURRENT_NODE.value: State.AT_INTERSECTION_TO_LOAD.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.AT_INTERSECTION_TO_LOAD.value: {
                Transition.LEFT_TURN.value: State.TURNING_LEFT_TO_LOAD.value,
                Transition.FORWARD_TURN.value: State.TURNING_FORWARD_TO_LOAD.value,
                Transition.RIGHT_TURN.value: State.WALL_FOLLOWING_TO_LOAD.value,
                Transition.WAIT_LOAD_ZONE.value: State.AT_LOAD_ZONE_TO_LOAD.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.TURNING_LEFT_TO_LOAD.value: {
                Transition.TURN_OVER.value: State.WALL_FOLLOWING_TO_LOAD.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.TURNING_FORWARD_TO_LOAD.value: {
                Transition.TURN_OVER.value: State.WALL_FOLLOWING_TO_LOAD.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.WALL_FOLLOWING_TO_LOAD.value: {
                Transition.CURRENT_NODE.value: State.AT_INTERSECTION_TO_LOAD.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.AT_LOAD_ZONE_TO_LOAD.value: {
                Transition.LOAD_OVER.value: State.AT_INTERSECTION_TO_DEPOSIT.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.AT_INTERSECTION_TO_DEPOSIT.value: {
                Transition.LEFT_TURN.value: State.TURNING_LEFT_TO_DEPOSIT.value,
                Transition.FORWARD_TURN.value: State.TURNING_FORWARD_TO_DEPOSIT.value,
                Transition.RIGHT_TURN.value: State.WALL_FOLLOWING_TO_DEPOSIT.value,
                Transition.WAIT_DEPOSIT_ZONE.value: State.AT_DEPOSIT_ZONE_TO_DEPOSIT.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.TURNING_LEFT_TO_DEPOSIT.value: {
                Transition.TURN_OVER.value: State.WALL_FOLLOWING_TO_DEPOSIT.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.TURNING_FORWARD_TO_DEPOSIT.value: {
                Transition.TURN_OVER.value: State.WALL_FOLLOWING_TO_DEPOSIT.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.WALL_FOLLOWING_TO_DEPOSIT.value: {
                Transition.CURRENT_NODE.value: State.AT_INTERSECTION_TO_DEPOSIT.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
            State.AT_DEPOSIT_ZONE_TO_DEPOSIT.value: {
                Transition.DEPOSIT_OVER.value: State.AT_INTERSECTION_TO_LOAD.value,
                Transition.BACK_TO_INIT.value: State.INITIAL.value,
            },
        }
