import time
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
import sys

WEBAPP_URL = f"http://127.0.0.1:{PORT}"

WEB_AND_ROSBRIDGE_CMD = (
    "source install/setup.bash && ros2 launch web_interface web_interface_launch.py"
)

TEXT_LOADED = "Chargé"
TEXT_NOT_LOADED = "Pas chargé"
ICON_REFERENCE = ".mdi-package"


@pytest.fixture(scope="module", autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


def test_web_updates_map_manager():
    build_web_interface()

    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)

    wait_for_server(WEBAPP_URL)

    from unittest.mock import MagicMock

    sys.modules["Jetson"] = MagicMock()
    sys.modules["Jetson.GPIO"] = MagicMock()
    from proximity_sensor.proximity_sensor_node import ProximitySensorNode

    proximity_sensor_node = ProximitySensorNode()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        page.wait_for_timeout(2000)

        rover_chip = page.locator(".v-chip").filter(has=page.locator(ICON_REFERENCE))

        expect(rover_chip).to_have_text(TEXT_NOT_LOADED, timeout=5000)

        proximity_sensor_node.gpio_from_1_to_0()

        start = time.time()
        while time.time() - start < 3:
            rclpy.spin_once(proximity_sensor_node, timeout_sec=0.1)

        expect(rover_chip).to_have_text(TEXT_LOADED, timeout=5000)

        page.wait_for_timeout(3000)

        browser.close()

    stop_process(web_and_rosbridge)
