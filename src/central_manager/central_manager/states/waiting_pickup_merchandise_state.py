from yasmin import State


class WaitingPickupMerchandiseState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "merchandise_loaded",
            "continue"
        ])

    def execute(self, blackboard):
        node = blackboard["node"]

        active_enforcers = [
            "stop_enforcer"
        ]

        if blackboard["active_enforcers"] != active_enforcers:
            blackboard["active_enforcers"] = active_enforcers
            node.publish_active_enforcers(active_enforcers)

        if blackboard["merchandise_present_flag"]:
            return "merchandise_loaded"

        return "continue"