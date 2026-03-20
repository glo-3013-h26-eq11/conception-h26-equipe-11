from yasmin import State


class TurningLeftState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "turn_complete",
            "continue"
        ])

    def execute(self, blackboard):
        node = blackboard["node"]

        #Liste à changer selon les enforcers finaux
        active_enforcers = [
            "left_turn_enforcer"
        ]

        if blackboard["active_enforcers"] != active_enforcers:
            blackboard["active_enforcers"] = active_enforcers
            node.publish_active_enforcers(active_enforcers)

        if blackboard["turn_complete_flag"]:
            blackboard["turn_complete_flag"] = False
            return "turn_complete"

        return "continue"