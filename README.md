# x2gbfs

x2gbfs is a library, which generates GBFS feed's from various providers.

Currently supported providers:
* deer (via it's fleetster API)


To generate a feed for e.g. deer network, execute

```sh
DEER_API_URL=URL DEER_USER=USER DEER_PASSWORD=PASSWORD python -m x2gbfs.x2gbfs -p deer -b 'file:out'
```

where `URL`, `USER` and `PASSWORD` needs to be replaced by the fleetster API credentials. 
Alternativly, these vars can be provided via an `.env` file in the current dir, 
which will be picked up by `x2gbfs`. 

Note: Usually, not every GBFS information can be retrieved from the provider's API. 
The content of `system_information` and `system_pricing_plans` currently needs to 
be provided via config/<provider>.json and need to be updated when that information changes.

## Implementing a new provider
To implement a new provider, you should take the following steps:

* Implement a new `BaseProvider` subclass, which retrieves `station_info`, `station_status`, `vehicles` and `vehicle_types` from the provides API.
* Provide a `config/my_new_provider.json` which contains a `feed_data` section that provides the seldomly updated `system_information` and `pricing_plans`.

Note that you should regularly check, if system or pricing information has changed and needs to be updated. 
To take notice of such changes, you might register a watch on the relevant urls of the provider website.

## Using Docker

To start x2gbfs in a docker container which runs indefinetly and updates all feeds every 30 seconds, start it e.g. like this, providing the interval lenght via `-i <secondsToWait>`:
```sh
docker build -t x2gbfs .
docker run --rm -v $PWD/out:/usr/src/app/out x2gbfs -p deer -b 'file:out' -i 30
```


## Documentation

### Provider's API documentation

* [fleetster-API-Documentation](https://my.fleetster.net/swagger/)

