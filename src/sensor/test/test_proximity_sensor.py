import pytest
import rclpy
import sys
from std_msgs.msg import Bool


@pytest.fixture(scope="module", autouse=True)
def rclpy_context():
    rclpy.init()
    yield
    rclpy.shutdown()


@pytest.fixture()
def fake_gpio(monkeypatch):
    fake_gpio = FakeGPIO()
    monkeypatch.setitem(sys.modules, "Jetson.GPIO", fake_gpio)

    if "sensor.proximity_sensor" in sys.modules:
        del sys.modules[
            "sensor.proximity_sensor"
        ]  # méthode batarde pour forcer de reload les modules pour le monkeypatch

    return fake_gpio


def test_when_transition_up_then_publishes_no_merchandise(fake_gpio):
    # Arrange
    from sensor.proximity_sensor import (
        ProximitySensor,
    )  # import nécessaire ici pour override le Jetson.GPIO
    from sensor.proximity_sensor import MerchandiseFlag
    from sensor.proximity_sensor import GPIO_PIN

    node = ProximitySensor()

    received_msgs = []

    def capture_callback(msg):
        flag = MerchandiseFlag(msg.data)
        received_msgs.append(flag)

    node.create_subscription(Bool, "is_there_merchandise", capture_callback, 10)

    # Act
    fake_gpio.set_input(1)
    fake_gpio.fire_transition_event(GPIO_PIN, fake_gpio.BOTH)

    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert len(received_msgs) == 1
    assert received_msgs[0] == MerchandiseFlag.NOT_DETECTED

    node.destroy_node()


def test_when_transition_down_then_publishes_there_is_merchandise(fake_gpio):
    # Arrange
    from sensor.proximity_sensor import (
        ProximitySensor,
    )  # import nécessaire ici pour override le Jetson.GPIO
    from sensor.proximity_sensor import MerchandiseFlag
    from sensor.proximity_sensor import GPIO_PIN

    node = ProximitySensor()

    received_msgs = []

    def capture_callback(msg):
        flag = MerchandiseFlag(msg.data)
        received_msgs.append(flag)

    node.create_subscription(Bool, "is_there_merchandise", capture_callback, 10)

    # Act
    fake_gpio.set_input(0)
    fake_gpio.fire_transition_event(GPIO_PIN, fake_gpio.BOTH)

    rclpy.spin_once(node, timeout_sec=0.1)

    # Assert
    assert len(received_msgs) == 1
    assert received_msgs[0] == MerchandiseFlag.IS_DETECTED

    node.destroy_node()


class FakeGPIO:

    BOARD = "BOARD"
    IN = "IN"
    BOTH = "BOTH"

    def __init__(self):
        self.callbacks = {}

    def setmode(self, mode):
        pass

    def set_input(self, input):
        self.input_value = input

    def setup(self, pin, direction):
        pass

    def input(self, pin):
        return self.input_value

    def add_event_detect(self, pin, transition_event, callback, bouncetime):
        self.callbacks[(pin, transition_event)] = callback

    def cleanup(self):
        pass

    def fire_transition_event(self, pin, transition_event):
        callback = self.callbacks[(pin, transition_event)]
        callback(pin)
