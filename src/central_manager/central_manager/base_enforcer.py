from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist


class Enforcer(ABC):
    @staticmethod
    def stop_robot(cmd: Twist) -> Twist:
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        return cmd

    @abstractmethod
    def enforce_cmd(self, cmd: Twist) -> Twist:
        pass
