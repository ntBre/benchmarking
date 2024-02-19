import json
import logging
import os
import time
import warnings
from dataclasses import dataclass

import click
import numpy
import pandas
import seaborn as sea
from ibstore import MoleculeStore
from matplotlib import pyplot
from openff.qcsubmit.results import OptimizationResultCollection
from openff.units import unit

# try to suppress stereo warnings - from lily's valence-fitting
# curate-dataset.py
logging.getLogger("openff").setLevel(logging.ERROR)

# suppress divide by zero in numpy.log
warnings.filterwarnings(
    "ignore", message="divide by zero", category=RuntimeWarning
)


@dataclass
class CachedResult:
    """All of the fields necessary to emulate
    MoleculeStore.from_qcsubmit_collection without calling
    OptimizationResultCollection.to_records

    """

    mapped_smiles: str
    inchi_key: str
    coordinates: numpy.ndarray
    qc_record_id: int
    qc_record_final_energy: float

    def to_dict(self):
        assert self.coordinates.units == unit.angstrom
        return dict(
            mapped_smiles=self.mapped_smiles,
            inchi_key=self.inchi_key,
            # this is a pint.Quantity-wrapped numpy array
            coordinates=self.coordinates.magnitude.tolist(),
            qc_record_id=self.qc_record_id,
            qc_record_final_energy=self.qc_record_final_energy,
        )


class CachedResultCollection:
    inner: list[CachedResult]

    def __init__(self):
        self.inner = []

    @classmethod
    def from_qcsubmit_collection(
        cls, collection: OptimizationResultCollection
    ):
        import qcelemental
        from tqdm import tqdm

        hartree2kcalmol = qcelemental.constants.hartree2kcalmol

        ret = cls()
        for qcarchive_record, molecule in tqdm(
            collection.to_records(),
            desc="Converting records to molecules",
        ):
            ret.inner.append(
                CachedResult(
                    mapped_smiles=molecule.to_smiles(
                        mapped=True, isomeric=True
                    ),
                    inchi_key=molecule.to_inchi(fixed_hydrogens=True),
                    coordinates=molecule.conformers[0],
                    qc_record_id=qcarchive_record.id,
                    qc_record_final_energy=qcarchive_record.get_final_energy()
                    * hartree2kcalmol,
                )
            )
        return ret

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.inner, default=CachedResult.to_dict, **kwargs)

    @classmethod
    def from_json(cls, filename):
        """Load a `CachedResultCollection` from `filename`"""
        with open(filename) as inp:
            data = json.load(inp)

        ret = cls()
        for entry in data:
            ret.inner.append(
                CachedResult(
                    mapped_smiles=entry["mapped_smiles"],
                    inchi_key=entry["inchi_key"],
                    coordinates=numpy.array(entry["coordinates"])
                    * unit.angstrom,
                    qc_record_id=entry["qc_record_id"],
                    qc_record_final_energy=entry["qc_record_final_energy"]
                    * unit.kilocalorie_per_mole,
                )
            )
        return ret


@click.command()
@click.option("--forcefield", "-f", default="force-field.offxml")
@click.option("--dataset", "-d", default="datasets/industry.json")
@click.option("--sqlite-file", "-s", default="tmp.sqlite")
@click.option("--out-dir", "-o", default=".")
@click.option("--procs", "-p", default=16)
@click.option("--invalidate-cache", "-i", is_flag=True, default=False)
def main(forcefield, dataset, sqlite_file, out_dir, procs, invalidate_cache):
    if invalidate_cache and os.path.exists(sqlite_file):
        os.remove(sqlite_file)
    if os.path.exists(sqlite_file):
        print(f"loading existing database from {sqlite_file}")
        store = MoleculeStore(sqlite_file)
    else:
        print(f"loading initial dataset from {dataset}")
        opt = OptimizationResultCollection.parse_file(dataset)

        print(f"generating database, saving to {sqlite_file}")
        store = MoleculeStore.from_qcsubmit_collection(opt, sqlite_file)

    print("started optimizing store")
    start = time.time()
    store.optimize_mm(force_field=forcefield, n_processes=procs)
    print(f"finished optimizing after {time.time() - start} sec")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    store.get_dde(forcefield).to_csv(f"{out_dir}/dde.csv")
    store.get_rmsd(forcefield).to_csv(f"{out_dir}/rmsd.csv")
    store.get_tfd(forcefield).to_csv(f"{out_dir}/tfd.csv")

    plot(out_dir)


def plot(out_dir, in_dirs=None, names=None, filter_records=None, negate=False):
    """Plot each of the `dde`, `rmsd`, and `tfd` CSV files found in `in_dirs`
    and write the resulting PNG images to out_dir. If provided, take the plot
    legend entries from `names` instead of `in_dirs`. If `filter_records` is
    provided, restrict the plot only to those records. `negate` swaps the
    comparison to include only the records *not* in `filter_records`.

    """
    # assume the input is next to the desired output
    if in_dirs is None:
        in_dirs = [out_dir]

    # default to directory names
    if names is None:
        names = in_dirs

    x_ranges = {
        "dde": (-6.0, 6.0),
        "rmsd": (-2.0, 0.7),
        "tfd": (-4.0, 0.5),
    }
    for dtype in ["step_dde", "dde", "rmsd", "tfd"]:
        figure, axis = pyplot.subplots(figsize=(6, 4))

        for name, in_dir in zip(names, in_dirs):
            if dtype == "step_dde":
                read = "dde"
            else:
                read = dtype
            dataframe = pandas.read_csv(f"{in_dir}/{read}.csv")
            dataframe = dataframe.rename(columns={"Unnamed: 0": "Record ID"})

            if filter_records is not None:
                if negate:
                    dataframe = dataframe[
                        ~dataframe["Record ID"]
                        .astype(str)
                        .isin(filter_records)
                    ]
                else:
                    dataframe = dataframe[
                        dataframe["Record ID"].astype(str).isin(filter_records)
                    ]

            if dtype == "dde":
                sea.kdeplot(
                    data=dataframe[dataframe.columns[-1]],
                    ax=axis,
                    label=name,
                )
                label = "DDE (kcal mol$^{-1}$)"
                axis.set_ylabel("Density")
                axis.set_xlim(x_ranges[dtype])
            elif dtype == "step_dde":
                counts, bins = numpy.histogram(
                    dataframe[dataframe.columns[-1]],
                    bins=numpy.linspace(-15, 15, 16),
                )

                axis.stairs(counts, bins, label=name)

                axis.set_ylabel("Count")
                label = "DDE (kcal mol$^{-1}$)"
            else:
                # for rmsd and tfd, we want the log KDE
                sorted_data = numpy.sort(
                    numpy.log10(dataframe[dataframe.columns[-1]])
                )
                sea.kdeplot(
                    data=sorted_data,
                    ax=axis,
                    label=name,
                )
                label = "Log " + dtype.upper()
                axis.set_ylabel("Density")
                axis.set_xlim(x_ranges[dtype])

            axis.set_xlabel(label)

        axis.legend(loc=0)

        pyplot.tight_layout()
        figure.savefig(f"{out_dir}/{dtype}.png", dpi=300)


if __name__ == "__main__":
    main()
