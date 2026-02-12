import pytest
from fastapi.testclient import TestClient
from web_interface.static_web_server import app
from web_interface.static_web_server import BASE_URL, PORT
import subprocess
import requests
import time

PACKAGE_NAME = "web_interface"
EXECUTABLE_NAME = "static_web_server"

URL = "http://" + BASE_URL + ":" + str(PORT)


@pytest.fixture()
def client():
    return TestClient(app=app)


@pytest.fixture()
def full_integration_ros_setup():
    subprocess.run(["npx", "vite", "build"], cwd="web_interface")
    subprocess.run(["colcon", "build"], cwd="../..", check=True)

    process = subprocess.Popen(
        f"source install/setup.bash && ros2 run {PACKAGE_NAME} {EXECUTABLE_NAME}",
        cwd="../..",
        shell=True,
        executable="/bin/bash",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    wait_for_server_response(process=process)
    yield
    terminate_server(process=process)


def wait_for_server_response(process):
    timeout = 10
    start = time.time()
    while True:
        try:
            r = requests.get(f"{URL}/")
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        if time.time() - start > timeout:
            process.terminate()
            raise TimeoutError("ROS2 server did not start in time")
        time.sleep(0.5)


def terminate_server(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def test_given_local_launch_when_get_index_then_return_200(client):
    response = client.get("/")

    assert response.status_code == 200


def test_given_ros_launch_when_get_index_then_return_200(full_integration_ros_setup):
    url = URL + "/"

    response = requests.get(url)

    assert response.status_code == 200
