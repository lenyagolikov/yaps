import argparse
import sys
import asyncio
import json
import pathlib
import csv

from tqdm import tqdm

from yaps.utils import logging
from yaps.es.schema import INDICES
from yaps.utils.db import connect_elasticsearch

logger = logging.get_logger("es_main")

main_parser = argparse.ArgumentParser(
    description="Initializing indices of ElasticSearch cluster "
    "and importing .csv data to it"
)
modes = main_parser.add_subparsers(
    title="Modes",
    dest="mode",
    description="mode of work of this module: init or import",
)
init_parser = modes.add_parser("init")
import_parser = modes.add_parser("import")
import_parser.add_argument("files", nargs="+", help="enumerating .csv files")

BULK_ACTIONS_COUNT = 300


async def main():
    elastic = connect_elasticsearch()

    args = main_parser.parse_args(sys.argv[1:])

    if args.mode == "init":
        logger.info("Starting initializing indices of ElasticSearch cluster...")
        for index in INDICES:
            name = index.Index.name
            if not await elastic.indices.exists(index=name):
                await elastic.indices.create(index=name, **index._index.to_dict())
                logger.info("Index %s has been created", name)

                # Settings for case when the free disk space is not enough
                await elastic.cluster.put_settings(
                    body={
                        "transient": {
                            "cluster.routing.allocation.disk.watermark.low": "3gb",
                            "cluster.routing.allocation.disk.watermark.high": "2gb",
                            "cluster.routing.allocation.disk.watermark.flood_stage": "1gb",
                            "cluster.info.update.interval": "1m",
                        }
                    }
                )
            else:
                logger.info("Index %s is already in the cluster", name)

    elif args.mode == "import":
        elastic.bulk_actions_count = BULK_ACTIONS_COUNT

        for file in args.files:
            logger.info("Index 'Product' begins to fill with data from '%s'...", file)
            f = pathlib.Path(file)
            reader = csv.DictReader(f.open(encoding="utf-8"))

            actions = []
            for row in tqdm(reader):
                id_ = row.pop("id")
                row["props"] = json.loads(row["props"])
                row["images"] = row["images"][1:-1].split(",")

                if len(actions) < BULK_ACTIONS_COUNT:
                    actions.append({"index": {"_index": "products", "_id": id_}})
                    actions.append(row)
                else:
                    await elastic.bulk(body=actions)
                    actions = []
            else:
                await elastic.bulk(body=actions)

        logger.info("Index 'Product' was filled successfully")

    await elastic.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
