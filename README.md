# x2gbfs

x2gbfs is a library, which generates GBFS feed's from various providers.

Currently supported providers:

* deer (via it's fleetster API, provider id: `deer`)
* VOI Karlsruhe (via Raumobil API, provider id: `voi-raumobil`)
* Stadtmobil Südbaden (via Cantamen IXSI API, provider id: `stadtmobil_suedbaden`)
* my-e-car (via Cantamen IXSI API, provider id: `my-e-car`)
* Lastenvelo Freiburg (via custom CSV, provider id: `lastenvelo_fr`)
* NOI OpenDataHub (provider id: `noi`)

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

Currently, a couple of providers are supported:

* deer, which uses Fleetster as backend provider,
* Lastenvelo Freiburg
* VOI Karlsruhe via backend provider Raumobil
* Stadtwerk Tauberfranken via backend provider MOQO
* Carsharing Südtirol via Nature Of Innovation (NOI)'s OpenDataHub
* Flinkster via db-connect API,
* and my-e-car, stadtmobil Südbaden and stadtmobil Stuttgart via backend provider Cantamen/IXSI.

### deer (Fleetster)

To generate the deer GBFS feed, you need to provide the following environment variables:

* `DEER_API_URL=https://deer.fleetster.de`
* `DEER_USER=<your username>`
* `DEER_PASSWORD=<your password>`

For details, see the [mapping documentation](./docs/mappings/deer_gbfs_2.3_mapping.md).


### Lastenvelo Freiburg (Custom)

Lastenvelo Freiburg publishes a regularly updated [CSV file](https://www.lastenvelofreiburg.de/LVF_usage.csv). No credentials are required.

For details, see the [mapping documentation](./docs/mappings/lastenvelo_fr_gbfs_2.3_mapping.md).


### Various Stadtmobil agencies and my-e-car (Cantamen)

To generate the stadtmobil_suedbaden, stadtmobil_stuttgart and my-e-car GBFS feed, you need to provide the following environment variables:

* `CANTAMEN_IXSI_API_URL=https://url.de`

Note: the Cantamen IXSI service is IP restricted.

For details, see the [mapping documentation](./docs/mappings/ixsi_gbfs_2.3_mapping.md).


### Cambio

Cambio provides publicly available static feeds for the cities they provide their service in.
Currently, only `cambio_aachen` is available. To extend `x2gbfs` for other cambio cities,
copy the config/cambio_aachen config and adapt accordingly.

Note that the pricing plans don't reflect the various available tarifs.

Note also, that Cambio asks users to only request their information once per 24 hours.

For details, see the [mapping documentation](./docs/mappings/cambio_gbfs_2.3_mapping.md).


### VOI (Raumobil)

To generate the voi raumobil GBFS feed, you need to provide the following environment variables:

* `VOI_API_URL=https://url.org`
* `VOI_USER=<your username>`
* `VOI_PASSWORD=<your password>`
 
### NOI OpenDataHub

Converts NOI's OpenDataHub carsharing feed to GBFS.



### Stadtwerk Tauberfranken (MOQO)

To generate the Stadtwerk Tauberfranken GBFS feed, you need to provide the following environment variable:

* `MOQO_API_TOKEN=<MOQO Token>`


### Flinkster (DB-Connect)

To generate the Flinkster GBFS feed, you need to provide the following environment variables:

* `FLINKSTER_CLIENT_ID=<FLINKSTER_CLIENT_ID>`
* `FLINKSTER_SECRET=<FLINKSTER_SECRET>`

### Free2move

To generate a GBFS feed for a Free2move location, you need to provide the following environment variables:

* `FREE2MOVE_BASE_URL=<FREE2MOVE_BASE_URL>`
* `FREE2MOVE_USER=<FREE2MOVE_USER>`
* `FREE2MOVE_PASSWORD=<FREE2MOVE_PASSWORD>`

Besides this, a CACHE_DIR env variable must be provided, which is used to store the last retrieved vehicles information, so only delta updates need to be requested.

For details, see the [mapping documentation](./docs/mappings/free2move_gbfs_2.3_mapping.md).


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
- runs indefinetly and updates all feeds every n seconds (`-i 60 or -i 3600`).

```sh
docker build -t x2gbfs .
# For dynamic feeds, update every 60 seconds (-i 60)
docker run --rm -v $PWD/out:/app/out --env-file .env x2gbfs -p deer,voi-raumobil,lastenvelo_fr,flinkster -b 'file:out' -i 60
# For static feeds, an update every hour (3600 seconds) should be sufficient (-i 3600)
docker run --rm -v $PWD/out:/app/out --env-file .env x2gbfs -p my-e-car,stadmobil_suedbaden -b 'file:out' -i 3600

```


## Documentation

### Provider's API documentation

* [fleetster-API-Documentation](https://my.fleetster.net/swagger/)
* [IXSI v5 - Interface for X-Sharing Information Version 5 Specification](https://carsharing.de/sites/default/files/uploads/ixsi-v5_docu_v0.9_bcs.pdf)
* [db-connect API](https://dbconnect-b2b-prod.service.dbrent.net/customer-b2b-api/docs/customer-b2b-api.html#resources-for-available-rental-objects-and-areas)