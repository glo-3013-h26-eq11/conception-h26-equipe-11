import time
import rclpy
from playwright.sync_api import sync_playwright
from web_interface.static_web_server import PORT
from integration_tests.integration_helper import (
    start_process,
    stop_process,
    wait_for_server,
    BoolTopicListener,
)

WEBAPP_URL = f"http://127.0.0.1:{PORT}"

START_BUTTON = "Démarrer le Rover"

ROS_TOPIC = "rover/start"

WEB_AND_ROSBRIDGE_CMD = (
    "source install/setup.bash && ros2 launch web_interface web_interface_launch.py"
)


def test_full_file_upload():

    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)

    wait_for_server(WEBAPP_URL)

    rclpy.init()
    listener = BoolTopicListener(ROS_TOPIC)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        page.get_by_role("button", name=START_BUTTON).click()

        page.wait_for_timeout(3000)

        browser.close()

    start = time.time()
    while time.time() - start < 10:
        rclpy.spin_once(listener, timeout_sec=0.1)

    listener.destroy_node()
    rclpy.shutdown()

    stop_process(web_and_rosbridge)

    assert len(listener.get_messages()) > 0, "No ROS messages received"
    print(f"Received {len(listener.get_messages())} processed messages")
