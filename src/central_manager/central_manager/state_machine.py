#!/usr/bin/env python3
from rclpy.node import Node
from yasmin import StateMachine
from threading import Thread

from central_manager.states.initial_state import InitialState

from central_manager.states.positioning.wall_following_positioning_state import (
    WallFollowingPositioningState,
)

from central_manager.states.to_load.at_intersection_to_load_state import (
    AtIntersectionToLoadState,
)
from central_manager.states.to_load.turning_left_to_load_state import (
    TurningLeftToLoadState,
)
from central_manager.states.to_load.turning_forward_to_load_state import (
    TurningForwardToLoadState,
)
from central_manager.states.to_load.wall_following_to_load_state import (
    WallFollowingToLoadState,
)
from central_manager.states.to_load.at_load_zone_to_load_state import AtLoadZoneToLoad

from central_manager.states.to_deposit.at_intersection_to_deposit_state import (
    AtIntersectionToDepositState,
)
from central_manager.states.to_deposit.turning_left_to_deposit_state import (
    TurningLeftToDepositState,
)
from central_manager.states.to_deposit.turning_forward_to_deposit_state import (
    TurningForwardToDepositState,
)
from central_manager.states.to_deposit.wall_following_to_deposit_state import (
    WallFollowingToDepositState,
)
from central_manager.states.to_deposit.at_deposit_zone_to_deposit_state import (
    AtDepositZoneToDeposit,
)


class StateMachineRover:
    def __init__(self, blackboard, node: Node):
        self.node = node

        self.blackboard = blackboard

        self.blackboard["node"] = node

        self.states = self.create_states(node)

        self.sm = self.create_state_machine()

    def run(self):
        outcome = self.sm(blackboard=self.blackboard)

        self.node.get_logger().info(f"FSM finished with outcome: {outcome}")

    def create_states(self, node):
        return {
            "INITIAL": InitialState(node),
            "WALL_FOLLOWING_POSITIONING": WallFollowingPositioningState(node),
            "AT_INTERSECTION_TO_LOAD": AtIntersectionToLoadState(node),
            "TURNING_LEFT_TO_LOAD": TurningLeftToLoadState(node),
            "TURNING_FORWARD_TO_LOAD": TurningForwardToLoadState(node),
            "WALL_FOLLOWING_TO_LOAD": WallFollowingToLoadState(node),
            "AT_LOAD_ZONE_TO_LOAD": AtLoadZoneToLoad(node),
            "AT_INTERSECTION_TO_DEPOSIT": AtIntersectionToDepositState(node),
            "TURNING_LEFT_TO_DEPOSIT": TurningLeftToDepositState(node),
            "TURNING_FORWARD_TO_DEPOSIT": TurningForwardToDepositState(node),
            "WALL_FOLLOWING_TO_DEPOSIT": WallFollowingToDepositState(node),
            "AT_LOAD_ZONE_TO_DEPOSIT": AtDepositZoneToDeposit(node),
        }

    def create_state_machine(self):
        sm = StateMachine(outcomes=["mission_complete", "error"])

        # Initial state
        sm.add_state(
            "INITIAL",
            self.states["INITIAL"],
            transitions={
                "system_ready": "WALL_FOLLOWING_POSITIONING",
            },
        )

        # Positioning state
        sm.add_state(
            "WALL_FOLLOWING_POSITIONING",
            self.states["WALL_FOLLOWING_POSITIONING"],
            transitions={
                "current_node": "AT_INTERSECTION_TO_LOAD",
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
            },
        )

        sm.add_state(
            "TURNING_LEFT_TO_LOAD",
            self.states["TURNING_LEFT_TO_LOAD"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_LOAD",
            },
        )

        sm.add_state(
            "TURNING_FORWARD_TO_LOAD",
            self.states["TURNING_FORWARD_TO_LOAD"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_LOAD",
            },
        )

        sm.add_state(
            "WALL_FOLLOWING_TO_LOAD",
            self.states["WALL_FOLLOWING_TO_LOAD"],
            transitions={
                "current_node": "AT_INTERSECTION_TO_LOAD",
            },
        )

        sm.add_state(
            "AT_LOAD_ZONE_TO_LOAD",
            self.states["AT_LOAD_ZONE_TO_LOAD"],
            transitions={
                "load_over": "AT_INTERSECTION_TO_DEPOSIT",
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
            },
        )

        sm.add_state(
            "TURNING_LEFT_TO_DEPOSIT",
            self.states["TURNING_LEFT_TO_DEPOSIT"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_DEPOSIT",
            },
        )

        sm.add_state(
            "TURNING_FORWARD_TO_DEPOSIT",
            self.states["TURNING_FORWARD_TO_DEPOSIT"],
            transitions={
                "turn_over": "WALL_FOLLOWING_TO_DEPOSIT",
            },
        )

        sm.add_state(
            "WALL_FOLLOWING_TO_DEPOSIT",
            self.states["WALL_FOLLOWING_TO_DEPOSIT"],
            transitions={
                "current_node": "AT_INTERSECTION_TO_DEPOSIT",
            },
        )

        sm.add_state(
            "AT_DEPOSIT_ZONE_TO_DEPOSIT",
            self.states["AT_DEPOSIT_ZONE_TO_DEPOSIT"],
            transitions={
                "deposit_over": "AT_INTERSECTION_TO_LOAD",
            },
        )

        return sm
