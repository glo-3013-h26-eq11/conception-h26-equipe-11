import rclpy
from std_msgs.msg import Bool
from rclpy.node import Node
import Jetson.GPIO as GPIO
from enum import Enum

GPIO_PIN = 7


class MerchandiseFlag(Enum):
    IS_DETECTED = True
    NOT_DETECTED = False


class ProximitySensor(Node):
    def __init__(self):
        super().__init__("proximity_sensor")
        self.publisher = self.create_publisher(Bool, "is_there_merchandise", 10)

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(GPIO_PIN, GPIO.IN)

        GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=self.gpio_from_0_to_1)

        GPIO.add_event_detect(GPIO_PIN, GPIO.FALLING, callback=self.gpio_from_1_to_0)

    def gpio_from_0_to_1(self, pin):
        boolean_msg = Bool()
        boolean_msg.data = MerchandiseFlag.NOT_DETECTED.value
        print("test change")
        self.publisher.publish(boolean_msg)

    def gpio_from_1_to_0(self, pin):
        boolean_msg = Bool()
        boolean_msg.data = MerchandiseFlag.IS_DETECTED.value
        print("test_change_other")
        self.publisher.publish(boolean_msg)


def main(args=None):
    rclpy.init(args=args)

    proximity_sensor = ProximitySensor()

    rclpy.spin(proximity_sensor)

    proximity_sensor.destroy_node()

    rclpy.shutdown()

    GPIO.cleanup(GPIO_PIN)


if __name__ == "__main__":
    main()
