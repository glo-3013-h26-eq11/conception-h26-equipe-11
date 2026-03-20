from yasmin import State


class WallFollowingState(State):
    def __init__(self):
        super().__init__(outcomes=[
            "intersection_detected",
            "loading_zone_detected",
            "continue"
        ])

    def execute(self, blackboard):
        node = blackboard["node"]
        
        #Liste à changer selon les enforcers finaux
        active_enforcers = [
            "wall_following_enforcer",
            "follow_vehicle_enforcer"
        ]

        if blackboard.get("active_enforcers") != active_enforcers:
            blackboard["active_enforcers"] = active_enforcers
            node.publish_active_enforcers(active_enforcers)

        if blackboard.get("intersection_transition_requested", default=False):
            blackboard["intersection_transition_requested"] = False
            return "intersection_detected"

        if blackboard.get("loading_zone_transition_requested", default=False):
            blackboard["loading_zone_transition_requested"] = False
            return "loading_zone_detected"

        return "continue"