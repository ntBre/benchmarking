import logging

import click
from openff.qcsubmit.results import OptimizationResultCollection

from cached_result import CachedResultCollection

logging.getLogger("openff").setLevel(logging.ERROR)


@click.command()
@click.option("--dataset", "-d", default="datasets/industry.json")
@click.option("--output", "-o", default="datasets/cache/industry.json")
def main(dataset, output):
    print("loading collection")
    opt = OptimizationResultCollection.parse_file(dataset)
    print("caching records")
    crc = CachedResultCollection.from_qcsubmit_collection(opt)

    print(f"serializing to json in {output}")
    with open(output, "w") as out:
        out.write(crc.to_json(indent=2))


if __name__ == "__main__":
    main()
