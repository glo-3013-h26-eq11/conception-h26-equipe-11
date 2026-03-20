from yasmin import State


class AtIntersectionState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "turn_left",
            "turn_forward",
            "turn_right",
            "continue"
        ])

    def execute(self, blackboard):
        node = blackboard["node"]

        #Liste à changer selon les enforcers finaux
        active_enforcers = [
            "stop_enforcer"
        ]

        if blackboard["active_enforcers"] != active_enforcers:
            blackboard["active_enforcers"] = active_enforcers
            node.publish_active_enforcers(active_enforcers)

        next_direction = blackboard["next_direction"]

        if next_direction == "left":
            return "turn_left"

        if next_direction == "straight":
            return "turn_forward"

        if next_direction == "right":
            return "turn_right"

        return "continue"