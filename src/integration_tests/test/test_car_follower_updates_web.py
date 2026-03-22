import rclpy
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


def test_car_follower_updates_web():
    build_web_interface()

    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)

    wait_for_server(WEBAPP_URL)

    enforcer_manager_node = EnforcerManagerNode()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        rover_chip = page.locator(".v-chip").filter(has=page.locator(ICON_REFERENCE))

        page.wait_for_timeout(2000)

        expect(rover_chip).to_have_text(TEXT_SAFE_DISTANCE, timeout=5000)

        enforcer_manager_node.publish_dangerous_distance()

        page.wait_for_timeout(2000)

        expect(rover_chip).to_have_text(TEXT_DANGEROUS_DISTANCE, timeout=5000)

        page.wait_for_timeout(3000)

        browser.close()

    stop_process(web_and_rosbridge)
