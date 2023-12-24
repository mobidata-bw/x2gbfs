# x2gbfs

x2gbfs is a library, which generates GBFS feed's from various providers.

Currently supported providers:

* deer (via it's fleetster API, provider id: `deer`)
* VOI Karlsruhe (via Raumobil API, provider id: `voi-raumobil`)
* Stadtmobil Südbaden (via Cantamen IXSI API, provider id: `stadtmobil_suedbaden`)
* my-e-car (via Cantamen IXSI API, provider id: `my-e-car`)
* Lastenvelo Freiburg (via custom CSV, provider id: `lastenvelo_fr`)

To generate a feed for e.g. deer network, switch to the `x2gbfs` project basee dir and execute

```sh
DEER_API_URL=URL DEER_USER=USER DEER_PASSWORD=PASSWORD python -m x2gbfs.x2gbfs -p deer -b 'file:out'
```

where `URL`, `USER` and `PASSWORD` needs to be replaced by the fleetster API credentials. 
If the GBFS has been generated successfully, this will result in the following output:

```
INFO:x2gbfs:Updated feeds for deer
```

Alternatively, the `DEER_API_URL`, `DEER_USER` and `DEER_PASSWORD` vars can be provided via an `.env` file in the current dir, which will be picked up by `x2gbfs`. See [.env.example](.env.example) fas an example.


Note: Usually, not every GBFS information can be retrieved from the provider's API. 
The content of `system_information` and `system_pricing_plans` currently needs to 
be provided via config/<provider>.json and needs to be updated when that information changes.

## Available providers

Currently, a couple of providers are supported: deer, which uses Fleetster as backend provider, Lastenvelo Freiburg, VOI Karlsruhe via backend provider Raumobil, and my-e-car and Stadtmobil Südbaden via backend provider IXSI.

### deer (Fleetster)

To generate the deer GBFS feed, you need to provide the following environment variables:

* `DEER_API_URL=https://deer.fleetster.de`
* `DEER_USER=<your username>`
* `DEER_PASSWORD=<your password>`

For details, see the [mapping documentation](./docs/mappings/deer_gbfs_2.3_mapping.md).


### Lastenvelo Freiburg (Custom)

Lastenvelo Freiburg publishes a regularly updated [CSV file](https://www.lastenvelofreiburg.de/LVF_usage.csv). No credentials are required.

For details, see the [mapping documentation](./docs/mappings/lastenvelo_fr_gbfs_2.3_mapping.md).


### Stadtmobil Südbaden and my-e-car (Cantamen)

To generate the stadtmobil_suedbaden and my-e-car GBFS feed, you need to provide the following environment variables:

* `CANTAMEN_IXSI_API_URL=https://url.de`

Note: the Cantamen IXSI service is IP restricted.

For details, see the [mapping documentation](./docs/mappings/ixsi_gbfs_2.3_mapping.md).


### VOI (Raumobil)

To generate the voi raumobil GBFS feed, you need to provide the following environment variables:

* `VOI_API_URL=https://url.org`
* `VOI_USER=<your username>`
* `VOI_PASSWORD=<your password>`

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
docker run --rm -v $PWD/out:/app/out --env-file .env x2gbfs -p deer,my-e-car,stadmobil_suedbaden,voi-raumobil,lastenvelo_fr -b 'file:out' -i 60
```


## Documentation

### Provider's API documentation

* [fleetster-API-Documentation](https://my.fleetster.net/swagger/)
* [IXSI v5 - Interface for X-Sharing Information Version 5 Specification](https://carsharing.de/sites/default/files/uploads/ixsi-v5_docu_v0.9_bcs.pdf)

