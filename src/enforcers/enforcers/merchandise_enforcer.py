from enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist


class MerchandiseEnforcer(Enforcer):
    def __init__(self):
        self.load_detected: bool = False
        self.destination: str | None = None

    def enforce_cmd(self, cmd: Twist) -> Twist:
        if (
            self.load_detected
            and self.destination
            and self.destination.startswith("ZC")
        ):
            return self.stop_robot(cmd)
        return cmd
