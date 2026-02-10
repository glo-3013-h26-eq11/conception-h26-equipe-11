from city_api.city_interface import CityInterface
import pytest
import requests


@pytest.fixture()
def wrong_url():
    CityInterface.set_url("http://localhost")
    return


def test_given_wrong_connection_when_get_then_raises_httperror(wrong_url):
    with pytest.raises(requests.exceptions.HTTPError):
        CityInterface.get()
