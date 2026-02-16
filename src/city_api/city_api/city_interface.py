import requests


class CityInterface:

    def __init__(self):
        self.URL = "http://designiii.ca/"

    def set_url(self, url: str):
        self.URL = url

    def get(self):
        response = requests.get(url=self.URL)

        response.raise_for_status()

    def get_cranes(self):
        response = requests.get(url=self.URL + "cranes")

        response.raise_for_status()

        return response.json()

    def get_crane_with_id(self, id: int):
        response = requests.get(url=self.URL + "cranes/" + str(id))

        response.raise_for_status()

        return response.json()

    def post_crane_with_id(self, id: int, nb_token: int):
        data = {"nb_tokens": nb_token}

        response = requests.post(url=self.URL + "cranes/" + str(id), json=data)

        response.raise_for_status()

    def get_vehicles(self):
        response = requests.get(url=self.URL + "vehicles")

        response.raise_for_status()

        return response.json()

    def get_vehicle_with_id(self, id: int):
        response = requests.get(url=self.URL + "vehicles/" + str(id))

        response.raise_for_status()

        return response.json()

    def post_vehicle_with_id(self, id: int, path: list[str]):
        data = {"path": path}

        response = requests.post(url=self.URL + "vehicles/" + str(id), json=data)

        response.raise_for_status()
