import json
from typing import Dict, Generator, Optional

import requests


class FleetsterAPI:
    """
    Returns locations and vehicles from fleetster endppoint.

    fleetster-API-Documentation is available here:
    https://my.fleetster.net/swagger/
    """

    token: Optional[str] = None
    api_url: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

    def __init__(self, api_url: str, user: str, password: str) -> None:
        self.api_url = api_url
        self.user = user
        self.password = password

    def all_stations(self) -> Generator[Dict, None, None]:
        locations = self._get_with_authorization(f'{self.api_url}/locations')
        for location in locations:
            yield location

    def all_vehicles(self) -> Generator[Dict, None, None]:
        vehicles = self._get_with_authorization(f'{self.api_url}/vehicles')
        for vehicle in vehicles:
            yield vehicle

    def all_bookings_ending_after(self, timestamp):
        enddate = timestamp.isoformat()
        return self._get_with_authorization(f'{self.api_url}/bookings?endDate%5B%24gte%5D={enddate}Z')

    def _login(self) -> str:
        if self.token is None:
            endpoint = f'{self.api_url}/users/auth'
            body = {'email': self.user, 'password': self.password}
            response = requests.post(endpoint, json=body, timeout=10)
            response.raise_for_status()

            self.token = response.json()['_id']

        return self.token

    def _get_with_authorization(self, url: str) -> Dict:
        token = self._login()
        response = requests.get(url, headers={'Authorization': token}, timeout=10)
        response.raise_for_status()

        return response.json()
