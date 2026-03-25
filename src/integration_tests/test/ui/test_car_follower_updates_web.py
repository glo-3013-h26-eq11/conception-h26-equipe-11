import rclpy
from rclpy.executors import SingleThreadedExecutor
import time
from rclpy.node import Node
from playwright.sync_api import sync_playwright, expect
from web_interface.static_web_server import PORT
from integration_tests.integration_helper import (
    wait_for_server,
    start_process,
    stop_process,
    build_web_interface,
)
import pytest
from central_manager.enforcer_manager_node import EnforcerManagerNode
from std_msgs.msg import Bool

WEBAPP_URL = f"http://127.0.0.1:{PORT}"

WEB_AND_ROSBRIDGE_CMD = (
    "source install/setup.bash && ros2 launch web_interface web_interface_launch.py"
)


TEXT_SAFE_DISTANCE = "Rover distance sécuritaire"
TEXT_DANGEROUS_DISTANCE = "Rover trop proche"
ICON_REFERENCE = ".mdi-alert"


@pytest.fixture(scope="module", autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()

@pytest.fixture()
def node():
    node : Node = EnforcerManagerNode()
    yield node
    node.destroy_node()

def test_car_follower_updates_web(node):
    build_web_interface()

    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)

    wait_for_server(WEBAPP_URL)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        rover_chip = page.locator(".v-chip").filter(has=page.locator(ICON_REFERENCE))

        page.wait_for_timeout(2000)

        expect(rover_chip).to_have_text(TEXT_SAFE_DISTANCE, timeout=5000)

        publisher = node.create_publisher(
            Bool, "/car_follower/dangerous_distance", 10
        )

        data = Bool()
        data.data = True
        publisher.publish(data)

        page.wait_for_timeout(3000)

        executor = SingleThreadedExecutor()
        executor.add_node(node)

        start = time.time()
        while time.time() - start < 4:
            executor.spin_once(timeout_sec=0.1)

        expect(rover_chip).to_have_text(TEXT_DANGEROUS_DISTANCE, timeout=5000)

        page.wait_for_timeout(3000)

        browser.close()

    stop_process(web_and_rosbridge)
