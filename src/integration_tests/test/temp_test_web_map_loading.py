import os
import signal
import subprocess
import time
from pathlib import Path

import pytest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from playwright.sync_api import sync_playwright

# =============================
# CONFIG — EDIT THESE
# =============================

WEBAPP_URL = "http://127.0.0.1:5555"

UPLOAD_TOPOGRAPHIE_SELECTOR = "Topographie"
UPLOAD_ARUCO_SELECTOR = "ArUco"
UPLOAD_BUTTON = "Téléchargé"

ROS_TOPIC = "map_manager/parsed_map_topic"

CSV_DIR = os.path.join(Path(__file__).parent, "ressources")
CSV_FILE_TOPOGRAPHIE = os.path.join(CSV_DIR, "topo_gros_cacouna.csv")
CSV_FILE_ARUCO = os.path.join(CSV_DIR, "aruco_gros_cacouna.csv")

WEB_AND_ROSBRIDGE_CMD = ["ros2", "launch", "web_interface", "web_interface_launch.py"]
ROS_NODE_CMD = ["ros2", "run", "navigation", "map_processor_node"]


# =============================
# ROS Listener
# =============================


class TopicListener(Node):
    def __init__(self):
        super().__init__("e2e_test_listener")
        self.messages = []
        self.create_subscription(String, ROS_TOPIC, self.callback, 10)

    def callback(self, msg):
        self.messages.append(msg.data)


# =============================
# Helpers
# =============================


def start_process(cmd, cwd=None):
    return subprocess.Popen(cmd, 
                            cwd=cwd,
                            shell=True,
                            executable="/bin/bash",
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, 
                            preexec_fn=os.setsid)


def stop_process(proc):
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


# =============================
# Test
# =============================

def test_full_file_upload():

    # Start backend services
    web_and_rosbridge = start_process(WEB_AND_ROSBRIDGE_CMD)
    rosnode = start_process(ROS_NODE_CMD)

    time.sleep(8)

    # Start ROS listener
    rclpy.init()
    listener = TopicListener()

    # Launch browser automation
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(WEBAPP_URL)

        page.get_by_label(UPLOAD_TOPOGRAPHIE_SELECTOR).set_input_files(
            CSV_FILE_TOPOGRAPHIE
        )
        page.get_by_label(UPLOAD_ARUCO_SELECTOR).set_input_files(CSV_FILE_ARUCO)

        page.get_by_role("button", name=UPLOAD_BUTTON).click()

        page.wait_for_timeout(3000)

        browser.close()

    # Wait for ROS messages
    start = time.time()
    while time.time() - start < 10:
        rclpy.spin_once(listener, timeout_sec=0.1)

    # Cleanup
    listener.destroy_node()
    rclpy.shutdown()

    stop_process(rosnode)
    stop_process(web_and_rosbridge)

    # Assertions
    assert len(listener.messages) > 0, "No ROS messages received"
    print(f"Received {len(listener.messages)} processed messages")
