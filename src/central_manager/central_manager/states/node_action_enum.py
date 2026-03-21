from enum import Enum


class NodeAction(Enum):
    LEFT_TURN = "left"
    RIGHT_TURN = "right"
    FORWARD_TURN = "forward"

    WAIT_DEPOSIT_ZONE = "deposit"
    WAIT_LOAD_ZONE = "load"
