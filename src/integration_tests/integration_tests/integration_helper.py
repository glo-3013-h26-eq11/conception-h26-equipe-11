import subprocess
import os
import signal
import time
import requests
from std_msgs.msg import Bool, String
from rclpy.node import Node


def build_web_interface(cwd="../.."):
    result = subprocess.run(
        "cd src/web_interface/web_interface && npx vite build",
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
    )
    if result.returncode != 0:
        raise RuntimeError("Vite build failed")


def start_process(cmd, cwd="../.."):
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
        stdout=None,
        stderr=None,
        preexec_fn=os.setsid,
    )


def stop_process(proc):
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def wait_for_server(url, timeout=30, interval=0.3):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(interval)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s")


class BoolTopicListener(Node):
    def __init__(self, ros_topic):
        super().__init__("e2e_test_listener")
        self.messages = []
        self.create_subscription(Bool, ros_topic, self.callback, 10)

    def callback(self, msg):
        self.messages.append(msg)

    def get_messages(self):
        return self.messages


class StringTopicListener(Node):
    def __init__(self, ros_topic):
        super().__init__("e2e_test_listener")
        self.messages = []
        self.create_subscription(String, ros_topic, self.callback, 10)

    def callback(self, msg):
        self.messages.append(msg)

    def get_messages(self):
        return self.messages
