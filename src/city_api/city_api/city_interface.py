import requests


class CityInterface:
    URL = "http://designiii.ca/"

    def set_url(url: str):
        CityInterface.URL = url

    def get():
        response = requests.get(url=CityInterface.URL)

        response.raise_for_status()

    def get_cranes():
        response = requests.get(url=CityInterface.URL + "cranes")

        response.raise_for_status()

        return response.json()

    def get_crane_with_id(id: int):
        response = requests.get(url=CityInterface.URL + "cranes/" + str(int))

        response.raise_for_status()

        return response.json()

    def get_vehicles():
        response = requests.get(url=CityInterface.URL + "vehicles")

        response.raise_for_status()

        return response.json()

    def get_vehicle_with_id(id: int):
        response = requests.get(url=CityInterface.URL + "vehicles/" + str(int))

        response.raise_for_status()

        return response.json()

    def post_vehicle_with_id(id: int, path: list[str]):
        data = {"path": path}

        response = requests.post(
            url=CityInterface.URL + "vehicles/" + str(int), json=data
        )

        response.raise_for_status()
