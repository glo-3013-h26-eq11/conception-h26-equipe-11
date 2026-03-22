from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
from rclpy.node import Publisher
from proximity_sensor.merchandise_flag import MerchandiseFlag

STOP_AFTER_DEPOSIT_DURATION = 1.5  # s


class WaitAtDepositEnforcer(Enforcer):
    def __init__(self, deposit_over_publisher: Publisher):
        super().__init__()

        self.timer = 0

        self.merchandise_unloaded = False

        self.deposit_over_publisher = deposit_over_publisher

    def update_with_real_speed(self, real_speed_cmd: Twist):

        if not self.merchandise_unloaded:
            return

        dt = self._compute_delta_time()

        self.timer += dt

    def enforce_cmd(self, cmd) -> Twist:
        if self.is_stop_after_deposit_over():
            self.deposit_over_publisher.publish(String())

        return Twist()

    def is_stop_after_deposit_over(self):
        return self.timer >= STOP_AFTER_DEPOSIT_DURATION

    def merchandise_callback(self, msg: Bool):
        transition = MerchandiseFlag(msg.data)

        if transition == MerchandiseFlag.UNLOADED:
            self.merchandise_unloaded = True
