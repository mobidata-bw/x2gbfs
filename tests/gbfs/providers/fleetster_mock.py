import json


class MockFleetsterAPI:
    """
    Returns static locations and vehicles from fleetster endppoint.

    TODO: as our credentials don't work, we currently use mock data

    fleetster-API-Documentation is available here:
    https://my.fleetster.net/swagger/
    """

    def all_stations(self):
        with open('tests/data/deer_locations.json') as location_file:
            locations = json.load(location_file)
            for location in locations:
                yield location

    def all_vehicles(self):
        with open('tests/data/deer_vehicles.json') as vehicles_file:
            vehicles = json.load(vehicles_file)
            for vehicle in vehicles:
                yield vehicle
