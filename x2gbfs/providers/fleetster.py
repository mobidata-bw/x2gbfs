import json
from typing import Optional
import requests


class FleetsterAPI:
    """
    Returns locations and vehicles from fleetster endppoint.

    fleetster-API-Documentation is available here:
    https://my.fleetster.net/swagger/
    """

    token: Optional[str] = None

    def __init__(self, api_url: str, user: str, password: str):
        self.api_url = api_url
        self.user = user
        self.password = password

    def login(self):
        if not self.token:
            endpoint = f'{self.api_url}/users/auth'
            body = {'email': self.user, 'password': self.password}
            response = requests.post(endpoint, json=body, timeout=10)
            if response.ok:
                self.token = response.json().get('_id')
            else:
                response.raise_for_status()

        return self.token

    def all_stations(self):
        locations = self._get_with_authorization(f'{self.api_url}/locations')
        for location in locations:
            yield location

    def all_vehicles(self):
        vehicles = self._get_with_authorization(f'{self.api_url}/vehicles')
        for vehicle in vehicles:
            yield vehicle

    def _get_with_authorization(self, url):
        token = self.login()
        response = requests.get(url, headers={'Authorization': token}, timeout=10)
        if response.ok:
            return response.json()

        response.raise_for_status()
        return None
