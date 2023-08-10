import numpy
import pandas
from ibstore import MoleculeStore
from matplotlib import pyplot
from openff.qcsubmit.results import OptimizationResultCollection


def main():
    ff = "force-field.offxml"
    opt = OptimizationResultCollection.parse_file(
        "../valence-fitting/02_curate-data/datasets/filtered-opt.json"
    )
    store = MoleculeStore.from_qcsubmit_collection(
        opt, database_name="tmp.sqlite"
    )

    store.optimize_mm(force_field=ff)
    store.get_dde(ff).to_csv("dde.csv")
    store.get_rmsd(ff).to_csv("rmsd.csv")
    store.get_tfd(ff).to_csv("tfd.csv")

    plot_cdfs()


def plot_cdfs(force_fields):
    x_ranges = {
        "dde": (-5.0, 5.0),
        "rmsd": (0.0, 4.0),
        "tfd": (0.0, 2.0),
    }
    for data in ["dde", "rmsd", "tfd"]:
        figure, axis = pyplot.subplots()
        for force_field in force_fields:
            dataframe = pandas.read_csv(f"{force_field}-{data}.csv")

            sorted_data = numpy.sort(dataframe[dataframe.columns[-1]])

            axis.plot(
                sorted_data,
                numpy.arange(1, len(sorted_data) + 1) / len(sorted_data),
                ".--",
                label=force_field,
            )

        axis.set_xlabel(data)
        axis.set_ylabel("CDF")

        axis.set_xlim(x_ranges[data])
        axis.set_ylim((0.0, 1.0))

        axis.legend(loc=0)

        figure.savefig(f"{data}.png")


if __name__ == "__main__":
    main()
