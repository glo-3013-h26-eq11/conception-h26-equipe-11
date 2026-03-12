from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist


class Enforcer(ABC):
    @staticmethod
    def stop_robot(cmd: Twist) -> Twist:
        stopped = Twist()
        # linear.x, angular.z default to 0.0 in a new Twist
        return stopped

    @abstractmethod
    def enforce_cmd(self, cmd: Twist) -> Twist:
        pass
