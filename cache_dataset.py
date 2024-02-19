import click
from openff.qcsubmit.results import OptimizationResultCollection

from cached_result import CachedResultCollection


@click.command()
@click.option("--dataset", "-d", default="datasets/industry.json")
@click.option("--output", "-o", default="datasets/cache/industry.json")
def main(dataset, output):
    opt = OptimizationResultCollection.parse_file(dataset)
    crc = CachedResultCollection.from_qcsubmit_collection(opt)

    with open(output, "w") as out:
        out.write(crc.to_json(indent=2))


if __name__ == "__main__":
    main()