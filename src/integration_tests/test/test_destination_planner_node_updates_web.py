import os
import time
from pathlib import Path
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
from rclpy.node import Node
from std_msgs.msg import String
import json

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
ROS_NODE_CMD_MIDDLE = (
    "source install/setup.bash && ros2 run navigation map_processor_node"
)
ROS_NODE_CMD_TARGET = (
    "source install/setup.bash && ros2 run navigation route_planner_node"
)

DESTINATION_LABEL = "Destination"
CURRENT_NODE = "ZD1"
GOAL_NODE = "ZC1"


@pytest.fixture(scope="module", autouse=True)
def ros_context():
    rclpy.init()
    yield
    rclpy.shutdown()


class TopicPublisher(Node):
    def __init__(self):
        super().__init__("topic_publisher")

        self.publisher_current_node = self.create_publisher(String, "current_node", 10)
        self.publisher_goal_node = self.create_publisher(String, "goal_node", 10)

    def publish_current_node(self):
        msg = String()
        data = {"id": CURRENT_NODE}
        msg.data = json.dumps(data)
        self.publisher_current_node.publish(msg)

    def publish_goal_node(self):
        msg = String()
        msg.data = GOAL_NODE
        self.publisher_goal_node.publish(msg)


def test_route_planner_node_updates_web():

    build_web_interface()
    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)
    rosnode_middle = start_process(ROS_NODE_CMD_MIDDLE)
    rosnode_target = start_process(ROS_NODE_CMD_TARGET)

    publisher_node = TopicPublisher()

    wait_for_server(WEBAPP_URL)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        page.wait_for_timeout(2000)

        page.locator("input[type='file']").nth(0).set_input_files(CSV_FILE_TOPOGRAPHIE)

        page.locator("input[type='file']").nth(1).set_input_files(CSV_FILE_ARUCO)

        page.get_by_role("button", name=UPLOAD_BUTTON).click()

        page.wait_for_timeout(3000)

        publisher_node.publish_goal_node()

        publisher_node.publish_current_node()

        start = time.time()
        while time.time() - start < 3:
            rclpy.spin_once(publisher_node, timeout_sec=0.1)

        expect(page.locator(".mdi-arrow-up")).to_be_visible()

        expect(page.locator(".mdi-arrow-left-top")).to_be_hidden()

        expect(page.locator(".mdi-arrow-right-top")).to_be_hidden()

        browser.close()

    publisher_node.destroy_node()

    stop_process(rosnode_middle)
    stop_process(rosnode_target)
    stop_process(web_and_rosbridge)
