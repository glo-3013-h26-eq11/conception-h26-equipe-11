from yasmin import State


class AtPickupZoneState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "stopped",
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

        if blackboard["zone_stop_complete_flag"]:
            blackboard["zone_stop_complete_flag"] = False
            return "stopped"

        return "continue"