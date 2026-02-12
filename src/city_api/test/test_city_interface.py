from city_api.city_interface import CityInterface
import pytest
import subprocess
import time
import requests

URL = "http://localhost:5000/"


@pytest.fixture(scope="session", autouse=True)
def start_design3_api():

    subprocess.run(
        [
            "sudo",
            "docker",
            "build",
            "--target",
            "dev",
            "-t",
            "design3-api",
            "./remote/design3-api",
        ],
        cwd="../..",
        check=True,
    )

    container = subprocess.run(
        ["sudo", "docker", "run", "-d", "-p", "5000:5000", "--rm", "design3-api"],
        check=True,
        capture_output=True,
        text=True,
    )

    container_id = container.stdout.strip()

    wait_for_server_response()

    yield

    subprocess.run(["sudo", "docker", "stop", container_id])
    subprocess.run(["sudo", "docker", "rm", container_id])


def wait_for_server_response():
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
            raise TimeoutError("docker local design3 server did not start in time")
        time.sleep(0.3)


@pytest.fixture()
def local_interface():
    interface = CityInterface()
    interface.set_url(URL)
    return interface


def test_given_when_get_from_local_city_api_then_doesnt_throw(local_interface):
    local_interface.get()


def test_given_when_get_cranes_from_local_city_api_then_returns_crane(local_interface):
    result = local_interface.get_cranes()

    assert "cranes" in result


def test_given_when_get_vehicles_from_local_city_api_then_returns_vehicles(
    local_interface,
):
    result = local_interface.get_vehicles()

    assert "vehicles" in result


def test_given_when_post_and_get_vehicle_with_id_from_local_city_api_then_returns_vehicles(
    local_interface,
):
    id = 1
    path = ["ZD7", "A1", "ZC1"]

    local_interface.post_vehicle_with_id(id, path)
    result = local_interface.get_vehicle_with_id(id)

    assert result["path"] == path
    assert result["id"] == id


def test_given_when_post_vehicle_with_invalid_id_then_throws_http_error(
    local_interface,
):
    id = 345654
    path = ["ZD7", "A1", "ZC1"]

    with pytest.raises(requests.HTTPError):
        local_interface.post_vehicle_with_id(id, path)


def test_given_when_post_and_get_crane_with_id_from_local_city_api_then_returns_cranes(
    local_interface,
):
    id = 1
    nb_tokens = 0

    local_interface.post_crane_with_id(id, nb_tokens)
    result = local_interface.get_crane_with_id(id)

    assert result["id"] == id
    assert result["nb_tokens"] == nb_tokens
