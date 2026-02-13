from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist

class Enforcer(ABC):
    @abstractmethod
    def enforce_cmd(self, cmd: Twist) -> Twist:
        pass
