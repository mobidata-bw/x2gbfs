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

* Implement a new `BaseProvider` subclass, which retrieves `station_info`, `station_status` (in case it's a station based system), `vehicles` and `vehicle_types` from the provides API.
* Provide a `config/my_new_provider.json` which contains a `feed_data` section that provides the seldomly updated `system_information` and `pricing_plans`.
* Add the newly created provider to `x2gbfs.py`'s `build_extractor` method.

Note that you should regularly check, if system or pricing information has changed and needs to be updated. 
To take notice of such changes, you might register a watch on the relevant urls of the provider website.

As an example, how a free floating provider could be implemented, see the [example provider](./x2gbfs/providers/example.py).

## Using Docker

The following command demonstrates how to run x2gbfs in a Docker container which
- only generates the `deer` GBFS feed (`-p deer`),
- writes into a directory that is mounted from the host machine (`-v …`),
- has access to the necessary Deer API credentials (`--env-file .env`),
- runs indefinetly and updates all feeds every 30 seconds (`-i 30`).

```sh
docker build -t x2gbfs .
docker run --rm -v $PWD/out:/app/out --env-file .env x2gbfs -p deer -b 'file:out' -i 30
```


## Documentation

### Provider's API documentation

* [fleetster-API-Documentation](https://my.fleetster.net/swagger/)

