import rclpy
from std_msgs.msg import Bool
import Jetson.GPIO as GPIO
from proximity_sensor.merchandise_flag import MerchandiseFlag
from web_interface.system_health_node import HealthPingingNode
import time
GPIO_PIN = 7


class ProximitySensorNode(HealthPingingNode):
    def __init__(self):
        super().__init__("proximity_sensor_node", "proximity_sensor")
        self.publisher = self.create_publisher(
            Bool, "/proximity_sensor/merchandise", 10
        )

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(GPIO_PIN, GPIO.IN)

        GPIO.add_event_detect(
            GPIO_PIN, GPIO.BOTH, callback=self.gpio_change, bouncetime=50
        )

    def gpio_change(self, pin):
        time.sleep(0.05)

        if GPIO.input(pin):
            self.gpio_from_0_to_1(pin)
        else:
            self.gpio_from_1_to_0(pin)

    def gpio_from_0_to_1(self, pin=7):
        boolean_msg = Bool()
        boolean_msg.data = MerchandiseFlag.UNLOADED.value
        self.publisher.publish(boolean_msg)
        self.get_logger().info("Merchandise : UNLOADED")

    def gpio_from_1_to_0(self, pin=7):
        boolean_msg = Bool()
        boolean_msg.data = MerchandiseFlag.LOADED.value
        self.publisher.publish(boolean_msg)
        self.get_logger().info("Merchandise : LOADED")



def main(args=None):
    rclpy.init(args=args)

    proximity_sensor = ProximitySensorNode()

    rclpy.spin(proximity_sensor)

    proximity_sensor.destroy_node()

    rclpy.shutdown()

    GPIO.cleanup(GPIO_PIN)


if __name__ == "__main__":
    main()
