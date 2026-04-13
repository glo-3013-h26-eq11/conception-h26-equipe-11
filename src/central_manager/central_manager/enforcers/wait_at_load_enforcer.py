from central_manager.enforcers.base_enforcer import Enforcer
from geometry_msgs.msg import Twist
from rclpy.node import Publisher
from std_msgs.msg import String, Bool
from proximity_sensor.merchandise_flag import MerchandiseFlag

STOP_AFTER_LOAD_DURATION = 0.8  # s


class WaitAtLoadEnforcer(Enforcer):
    def __init__(self, load_over_publisher: Publisher):
        super().__init__()

        self.timer = 0

        self.merchandise_loaded = False

        self.load_over_publisher = load_over_publisher

    def update_with_real_speed(self, real_speed_cmd: Twist):

        if not self.merchandise_loaded:
            return

        dt = self._compute_delta_time()

        self.timer += dt

    def enforce_cmd(self, cmd) -> Twist:
        if self.is_stop_after_load_over():
            self.load_over_publisher.publish(String())

        return Twist()

    def is_stop_after_load_over(self):
        return self.timer >= STOP_AFTER_LOAD_DURATION

    def merchandise_callback(self, msg: Bool):
        transition = MerchandiseFlag(msg.data)

        if transition == MerchandiseFlag.LOADED:
            self.merchandise_loaded = True
