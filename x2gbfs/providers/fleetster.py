import json
import logging
from datetime import datetime
from random import random
from time import sleep
from typing import Dict, Generator, Optional

import requests

logger = logging.getLogger(__name__)


class FleetsterAPI:
    """
    Returns locations and vehicles from fleetster endppoint.

    fleetster-API-Documentation is available here:
    https://my.fleetster.net/swagger/
    """

    #: Number of times a login is attempted before an error is thrown on 401 response
    MAX_LOGIN_ATTEMPTS = 5

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

    def all_bookings_ending_after(self, utctimestamp: datetime):
        enddate = self._timestamp_to_isoformat(utctimestamp)
        return self._get_with_authorization(f'{self.api_url}/bookings?endDate%5B%24gte%5D={enddate}')

    def _timestamp_to_isoformat(self, utctimestamp: datetime):
        """
        Returns timestamp in isoformat.
        As fleetster currently can't handle numeric timezone information, we replace +00:00 by Z
        """
        return utctimestamp.isoformat().replace('+00:00', 'Z')

    def _login(self) -> str:
        if self.token is None:
            endpoint = f'{self.api_url}/users/auth'
            body = {'email': self.user, 'password': self.password}
            response = requests.post(endpoint, json=body, timeout=10)
            response.raise_for_status()

            self.token = response.json()['_id']

        return self.token

    def _get_with_authorization(self, url: str) -> Dict:
        """
        Gets the provided url and returns the response as (json) dict.

        The request is performed with an authentication token, aquired before the request.
        In case the API responds with an 401 response, a new login is attempted
        self.MAX_LOGIN_ATTEMPTS times.
        """
        no_of_login_attempts = 0
        while not no_of_login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            no_of_login_attempts += 1
            token = self._login()
            response = requests.get(url, headers={'Authorization': token}, timeout=10)
            if response.status_code == 401:
                # Authentication issues will cause a retry attempt.
                # An authentication issue could be caused by a competing client requesting
                # a session token with the same credentials, invalidating our token

                # Give potentially competing clients some time to complete their requests
                # exponential back-offs plus some randomised "jitter" to prevent the https://en.wikipedia.org/wiki/Thundering_herd_problem
                seconds_to_sleep = (
                    0.5 * (1 + random() / 10) * no_of_login_attempts**2  # noqa: S311 (no cryptographic purpose)
                )
                logger.warn(
                    f'Requested token {self.token} was invalid, waiting for {seconds_to_sleep} seconds before retry'
                )
                sleep(seconds_to_sleep)

                # Reset authentication token, so it will be requested again
                self.token = None

            else:
                break

        response.raise_for_status()
        return response.json()
