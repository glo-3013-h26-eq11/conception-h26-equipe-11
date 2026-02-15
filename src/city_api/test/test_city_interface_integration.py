from city_api.city_interface import CityInterface


def test_when_get_cranes_from_remote_city_api_then_doesnt_throw():
    interface = CityInterface()

    interface.get_cranes()
