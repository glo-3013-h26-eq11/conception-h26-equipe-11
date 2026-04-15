from enum import Enum


class Transition(Enum):
    SYSTEM_READY = ("system_ready",)
    BACK_TO_INIT = ("back_to_init",)

    CURRENT_NODE = ("current_node",)

    LEFT_TURN = ("left_turn",)
    FORWARD_TURN = ("forward_turn",)
    RIGHT_TURN = ("right_turn",)
    TURN_OVER = ("turn_over",)

    WAIT_LOAD_ZONE = ("wait_load_zone",)
    WAIT_DEPOSIT_ZONE = ("wait_deposit_zone",)

    LOAD_OVER = ("load_over",)
    DEPOSIT_OVER = "deposit_over"
