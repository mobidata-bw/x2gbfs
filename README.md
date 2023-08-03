# x2gbfs

x2gbfs is a library, which generates GBFS feed's from various providers.

Currently supported providers:
* deer (via it's fleetster API)


To generate a feed for e.g. deer network, execute

```sh
DEER_API_URL=URL DEER_USER=USER DEER_PASSWORD=PASSWORD python -m x2gbfs.x2gbfs -c deer
```

where `URL`, `USER` and `PASSWORD` needs to be replaced by the fleetster API credentials.

Note: Not every GBFS information can be retrieved from the API. The content of `system_information` and `system_pricing_plans` is provided via config/deer.json and need to be updated when this information changes.

## Using Docker

```sh
docker build -t x2gbfs .
docker run --rm -v $PWD/out:/usr/src/app/out x2gbfs -p deer
```

## Documentation

fleetster-API-Documentation is available here: https://my.fleetster.net/swagger/
