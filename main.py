import os
import time

import numpy
import pandas
from ibstore import MoleculeStore
from matplotlib import pyplot
from openff.qcsubmit.results import OptimizationResultCollection
from openff.qcsubmit.results.filters import UnperceivableStereoFilter


def main():
    ff = "force-field.offxml"
    db_file = "tmp.sqlite"
    dataset = "../valence-fitting/02_curate-data/datasets/filtered-opt.json"

    if os.path.exists(db_file):
        print(f"loading existing database from {db_file}")
        store = MoleculeStore(db_file)
    else:
        print(f"loading initial dataset from {dataset}")
        opt = OptimizationResultCollection.parse_file(dataset)

        print("filtering by stereochemistry")
        opt = opt.filter(UnperceivableStereoFilter())

        print(f"generating database, saving to {db_file}")
        store = MoleculeStore.from_qcsubmit_collection(opt, db_file)

    print("started optimizing store")
    start = time.time()
    store.optimize_mm(force_field=ff)
    end = time.time()
    print(f"finished optimizing after {end - start} sec")

    store.get_dde(ff).to_csv("dde.csv")
    store.get_rmsd(ff).to_csv("rmsd.csv")
    store.get_tfd(ff).to_csv("tfd.csv")

    plot_cdfs()


def plot_cdfs():
    x_ranges = {
        "dde": (-5.0, 5.0),
        "rmsd": (0.0, 4.0),
        "tfd": (0.0, 2.0),
    }
    for data in ["dde", "rmsd", "tfd"]:
        figure, axis = pyplot.subplots()
        dataframe = pandas.read_csv(f"{data}.csv")

        sorted_data = numpy.sort(dataframe[dataframe.columns[-1]])

        axis.plot(
            sorted_data,
            numpy.arange(1, len(sorted_data) + 1) / len(sorted_data),
            ".--",
            label="Force Field",
        )

        axis.set_xlabel(data)
        axis.set_ylabel("CDF")

        axis.set_xlim(x_ranges[data])
        axis.set_ylim((0.0, 1.0))

        axis.legend(loc=0)

        figure.savefig(f"{data}.png")


if __name__ == "__main__":
    main()
