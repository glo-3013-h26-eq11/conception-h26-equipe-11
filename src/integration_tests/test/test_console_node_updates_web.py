import time
import rclpy
import pytest
from playwright.sync_api import sync_playwright, expect
from rclpy.node import Node
from web_interface.static_web_server import PORT
from integration_tests.integration_helper import (
    start_process,
    stop_process,
    wait_for_server,
    build_web_interface,
)
from rcl_interfaces.msg import Log

WEBAPP_URL = f"http://127.0.0.1:{PORT}"

WEB_AND_ROSBRIDGE_CMD = (
    "source install/setup.bash && ros2 launch web_interface web_interface_launch.py"
)

MESSAGE = "this is a test message"


@pytest.fixture(scope="module", autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


class RosoutPublisherTopic(Node):
    def __init__(self):
        super().__init__("publisher_node")

        self.publisher = self.create_publisher(Log, "/rosout", 10)

    def publish(self):
        msg = Log()
        msg.msg = MESSAGE
        msg.level = 10
        self.publisher.publish(msg)


def test_web_updates_start():

    build_web_interface()

    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)

    rosout_publisher_topic = RosoutPublisherTopic()

    wait_for_server(WEBAPP_URL)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        page.wait_for_timeout(2000)

        rosout_publisher_topic.publish()

        start = time.time()
        while time.time() - start < 2:
            rclpy.spin_once(rosout_publisher_topic, timeout_sec=0.1)

        expect(page.locator(".v-virtual-scroll__container")).to_contain_text(MESSAGE)

        browser.close()

    rosout_publisher_topic.destroy_node()

    stop_process(web_and_rosbridge)
