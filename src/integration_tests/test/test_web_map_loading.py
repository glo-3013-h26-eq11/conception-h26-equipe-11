import os
import time
from pathlib import Path
import rclpy
from playwright.sync_api import sync_playwright
from web_interface.static_web_server import PORT
from integration_tests.integration_helper import (
    wait_for_server,
    start_process,
    stop_process,
    StringTopicListener,
)

WEBAPP_URL = f"http://127.0.0.1:{PORT}"

UPLOAD_TOPOGRAPHIE_SELECTOR = "Topographie"
UPLOAD_ARUCO_SELECTOR = "ArUco"
UPLOAD_BUTTON = "Téléchargé"

ROS_TOPIC = "map_manager/parsed_map_topic"

CSV_DIR = os.path.join(Path(__file__).parent, "ressources")
CSV_FILE_TOPOGRAPHIE = os.path.join(CSV_DIR, "topo_gros_cacouna.csv")
CSV_FILE_ARUCO = os.path.join(CSV_DIR, "aruco_gros_cacouna.csv")

WEB_AND_ROSBRIDGE_CMD = (
    "source install/setup.bash && ros2 launch web_interface web_interface_launch.py"
)
ROS_NODE_CMD = "source install/setup.bash && ros2 run navigation map_processor_node"


def test_full_file_upload():

    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)
    rosnode = start_process(ROS_NODE_CMD)

    wait_for_server(WEBAPP_URL)

    rclpy.init()
    listener = StringTopicListener(ROS_TOPIC)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        page.locator("input[type='file']").nth(0).set_input_files(CSV_FILE_TOPOGRAPHIE)

        page.locator("input[type='file']").nth(1).set_input_files(CSV_FILE_ARUCO)

        page.get_by_role("button", name=UPLOAD_BUTTON).click()

        page.wait_for_timeout(3000)

        browser.close()

    start = time.time()
    while time.time() - start < 10:
        rclpy.spin_once(listener, timeout_sec=0.1)

    listener.destroy_node()
    rclpy.shutdown()

    stop_process(rosnode)
    stop_process(web_and_rosbridge)

    assert len(listener.messages) > 0, "No ROS messages received"
    print(f"Received {len(listener.messages)} processed messages")
