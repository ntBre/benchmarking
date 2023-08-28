import logging
import os
import time

import click
import numpy
import pandas
from ibstore import MoleculeStore
from matplotlib import pyplot
from openff.qcsubmit.results import OptimizationResultCollection

# try to suppress stereo warnings - from lily's valence-fitting
# curate-dataset.py
logging.getLogger("openff").setLevel(logging.ERROR)


@click.command()
@click.option("--forcefield", default="force-field.offxml")
@click.option("--dataset", default="datasets/industry.json")
@click.option("--db-file", default="tmp.sqlite")
@click.option("--out-dir", default=".")
def main(forcefield, dataset, db_file, out_dir):
    if os.path.exists(db_file):
        print(f"loading existing database from {db_file}")
        store = MoleculeStore(db_file)
    else:
        print(f"loading initial dataset from {dataset}")
        opt = OptimizationResultCollection.parse_file(dataset)

        print(f"generating database, saving to {db_file}")
        store = MoleculeStore.from_qcsubmit_collection(opt, db_file)

    print("started optimizing store")
    start = time.time()
    store.optimize_mm(force_field=forcefield, n_processes=16)
    end = time.time()
    print(f"finished optimizing after {end - start} sec")

    store.get_dde(forcefield).to_csv(f"{out_dir}/dde.csv")
    store.get_rmsd(forcefield).to_csv(f"{out_dir}/rmsd.csv")
    store.get_tfd(forcefield).to_csv(f"{out_dir}/tfd.csv")

    plot(out_dir)


def plot(out_dir, in_dirs=None, names=None):
    """
    Plot each of the `dde`, `rmsd`, and `tfd` CSV files found in
    `in_dirs` and write the resulting PNG images to out_dir. If
    provided, take the plot legend entries from `names` instead of
    `in_dirs`.
    """
    # assume the input is next to the desired output
    if in_dirs is None:
        in_dirs = [out_dir]

    # default to directory names
    if names is None:
        names = in_dirs

    x_ranges = {
        "dde": (-5.0, 5.0),
        "rmsd": (0.0, 4.0),
        "tfd": (0.0, 2.0),
    }
    for data in ["dde", "rmsd", "tfd"]:
        figure, axis = pyplot.subplots()

        for name, in_dir in zip(names, in_dirs):
            dataframe = pandas.read_csv(f"{in_dir}/{data}.csv")

            if data == "dde":
                counts, bins = numpy.histogram(
                    dataframe[dataframe.columns[-1]],
                    bins=numpy.linspace(-15, 15, 16),
                )

                axis.stairs(counts, bins, label=name)

                axis.set_ylabel("Count")
            else:
                sorted_data = numpy.sort(dataframe[dataframe.columns[-1]])

                axis.plot(
                    sorted_data,
                    numpy.arange(1, len(sorted_data) + 1) / len(sorted_data),
                    ".--",
                    label=name,
                )

                axis.set_xlim(x_ranges[data])
                axis.set_ylim((0.0, 1.0))

            label = dict(
                dde="DDE (kcal mol$^{-1}$)", rmsd="RMSD (Å)", tfd="TFD"
            )[data]
            axis.set_xlabel(label)
            axis.set_ylabel("CDF")

        axis.legend(loc=0)

        figure.savefig(f"{out_dir}/{data}.png", dpi=300)


if __name__ == "__main__":
    main()
