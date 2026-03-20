from yasmin import State


class InitialState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "system_ready",
            "continue"
        ])

    def execute(self, blackboard):
        node = blackboard["node"]

        active_enforcers = [
            "wall_following_enforcer",
            "follow_vehicle_enforcer"
        ]
        
        if blackboard["active_enforcers"] != active_enforcers:
            blackboard["active_enforcers"] = active_enforcers
            node.publish_active_enforcers(active_enforcers)
            
        if blackboard["system_ready_flag"]:
            blackboard["system_ready_flag"] = False
            return "system_ready"

        return "continue"