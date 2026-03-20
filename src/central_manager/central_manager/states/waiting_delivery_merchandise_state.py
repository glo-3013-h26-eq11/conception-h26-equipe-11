from yasmin import State


class WaitingDeliveryMerchandiseState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "merchandise_unloaded",
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

        if not blackboard["merchandise_present_flag"]:
            return "merchandise_unloaded"

        return "continue"