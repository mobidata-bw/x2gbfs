import json


class MockRaumobilAPI:
    """
    Returns static vehicles from raumobil endpoint.

    TODO: as our credentials don't work, we currently use mock data

    Raumobil Endpoint is available here:
    https://lsd.raumobil.net/
    """

    def all_vehicles(self):
        with open('tests/data/voi_raumobil_vehicles.json') as vehicles_file:
            results = json.load(vehicles_file)
            vehicles = results['result']['u0ty']['features']
            for vehicle in vehicles:
                yield vehicle
