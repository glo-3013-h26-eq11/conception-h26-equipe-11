from rclpy.node import Node
from yasmin import StateMachine

from central_manager.states.initial.initial_state import InitialState

from central_manager.states.to_load.at_intersection_to_load_state import (
    AtIntersectionToLoadState,
)
from central_manager.states.movement.turning_left_state import (
    TurningLeftState,
)
from central_manager.states.movement.turning_forward_state import (
    TurningForwardState,
)
from central_manager.states.movement.wall_following_state import (
    WallFollowingState,
)
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

        self.sm = self.create_state_machine()

    def run(self, blackboard):
        outcome = self.sm(blackboard=blackboard)

        self.node.get_logger().info(f"FSM finished with outcome: {outcome}")

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

    def create_state_machine(self):
        sm = StateMachine(outcomes=["mission_complete", "error"])

        # Initial state
        sm.add_state(
            "INITIAL",
            self.states["INITIAL"],
            transitions={
                "system_ready": "WALL_FOLLOWING_POSITIONING",
                "back_to_init": "INITIAL",
            },
        )

        # Positioning state
        sm.add_state(
            "WALL_FOLLOWING_POSITIONING",
            self.states["WALL_FOLLOWING_POSITIONING"],
            transitions={
                "current_node": "AT_INTERSECTION_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        )

        # To load state
        sm.add_state(
            "AT_INTERSECTION_TO_LOAD",
            self.states["AT_INTERSECTION_TO_LOAD"],
            transitions={
                "left_turn": "TURNING_LEFT_TO_LOAD",
                "forward_turn": "TURNING_FORWARD_TO_LOAD",
                "right_turn": "WALL_FOLLOWING_TO_LOAD",
                "wait_load_zone": "AT_LOAD_ZONE_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "TURNING_LEFT_TO_LOAD",
            self.states["TURNING_LEFT_TO_LOAD"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "TURNING_FORWARD_TO_LOAD",
            self.states["TURNING_FORWARD_TO_LOAD"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "WALL_FOLLOWING_TO_LOAD",
            self.states["WALL_FOLLOWING_TO_LOAD"],
            transitions={
                "current_node": "AT_INTERSECTION_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "AT_LOAD_ZONE_TO_LOAD",
            self.states["AT_LOAD_ZONE_TO_LOAD"],
            transitions={
                "load_over": "AT_INTERSECTION_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
        )

        # To deposit state
        sm.add_state(
            "AT_INTERSECTION_TO_DEPOSIT",
            self.states["AT_INTERSECTION_TO_DEPOSIT"],
            transitions={
                "left_turn": "TURNING_LEFT_TO_DEPOSIT",
                "forward_turn": "TURNING_FORWARD_TO_DEPOSIT",
                "right_turn": "WALL_FOLLOWING_TO_DEPOSIT",
                "wait_deposit_zone": "AT_DEPOSIT_ZONE_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "TURNING_LEFT_TO_DEPOSIT",
            self.states["TURNING_LEFT_TO_DEPOSIT"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "TURNING_FORWARD_TO_DEPOSIT",
            self.states["TURNING_FORWARD_TO_DEPOSIT"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "WALL_FOLLOWING_TO_DEPOSIT",
            self.states["WALL_FOLLOWING_TO_DEPOSIT"],
            transitions={
                "current_node": "AT_INTERSECTION_TO_DEPOSIT",
                "back_to_init": "INITIAL",
            },
        )

        sm.add_state(
            "AT_DEPOSIT_ZONE_TO_DEPOSIT",
            self.states["AT_DEPOSIT_ZONE_TO_DEPOSIT"],
            transitions={
                "deposit_over": "AT_INTERSECTION_TO_LOAD",
                "back_to_init": "INITIAL",
            },
        )

        return sm
