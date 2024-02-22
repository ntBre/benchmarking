import logging
import os
import time
import warnings
from collections import defaultdict

import click
import numpy
import pandas
import seaborn as sea
from ibstore import MoleculeStore
from ibstore._db import (
    DBMMConformerRecord,
    DBMoleculeRecord,
    DBQMConformerRecord,
    MMConformerRecord,
)
from matplotlib import pyplot

from cached_result import CachedResultCollection

# try to suppress stereo warnings - from lily's valence-fitting
# curate-dataset.py
logging.getLogger("openff").setLevel(logging.ERROR)

# suppress divide by zero in numpy.log
warnings.filterwarnings(
    "ignore", message="divide by zero", category=RuntimeWarning
)


def get_molecule_id_by_inchi_key(db, inchi_key):
    return {
        inchi_key: id
        for (id, inchi_key) in reversed(
            db.db.query(DBMoleculeRecord.id, DBMoleculeRecord.inchi_key).all()
        )
    }


# copy of MoleculeStore.optimize_mm with db session optimizations
def optimize_mm(
    store,
    force_field: str,
    prune_isomorphs: bool = False,
    n_processes: int = 2,
    chunksize=32,
):
    from ibstore._minimize import _minimize_blob

    inchi_keys = store.get_inchi_keys()

    _data = defaultdict(list)

    for inchi_key in inchi_keys:
        molecule_id = store.get_molecule_id_by_inchi_key(inchi_key)

        with store._get_session() as db:
            qm_conformers = [
                {
                    "qcarchive_id": record.qcarchive_id,
                    "mapped_smiles": record.mapped_smiles,
                    "coordinates": record.coordinates,
                }
                for record in db.db.query(
                    DBQMConformerRecord,
                )
                .filter_by(parent_id=molecule_id)
                .all()
            ]

            for qm_conformer in qm_conformers:
                if not db._mm_conformer_already_exists(
                    qcarchive_id=qm_conformer["qcarchive_id"],
                    force_field=force_field,
                ):
                    _data[inchi_key].append(qm_conformer)
                else:
                    pass

    if len(_data) == 0:
        return

    _minimized_blob = _minimize_blob(
        input=_data,
        force_field=force_field,
        prune_isomorphs=prune_isomorphs,
        n_processes=n_processes,
        chunksize=chunksize,
    )

    start = time.time()
    print("started storing records")

    # this time the dict gives the same result as the list, at least for my
    # small example, but I threw in a reversed just in case
    inchi_to_id = get_molecule_id_by_inchi_key(db, inchi_key)

    with store._get_session() as db:
        # from _mm_conformer_already_exists
        seen = set(
            db.db.query(
                DBMMConformerRecord.qcarchive_id,
            )
        )
        for result in _minimized_blob:
            inchi_key = result.inchi_key
            molecule_id = inchi_to_id[inchi_key]
            record = MMConformerRecord(
                molecule_id=molecule_id,
                qcarchive_id=result.qcarchive_id,
                force_field=result.force_field,
                mapped_smiles=result.mapped_smiles,
                energy=result.energy,
                coordinates=result.coordinates,
            )
            # inlined from MoleculeStore.store_conformer
            if record.qcarchive_id in seen:
                print("already seen this record, skipping")
                continue
            seen.add(record.qcarchive_id)
            db.store_mm_conformer_record(record)

        print(f"closing db session after {time.time() - start} sec")

    print(f"finished storing records after {time.time() - start} sec")


@click.command()
@click.option("--forcefield", "-f", default="force-field.offxml")
@click.option("--dataset", "-d", default="datasets/cache/industry.json")
@click.option("--sqlite-file", "-s", default="tmp.sqlite")
@click.option("--out-dir", "-o", default=".")
@click.option("--procs", "-p", default=16)
@click.option("--invalidate-cache", "-i", is_flag=True, default=False)
def main(forcefield, dataset, sqlite_file, out_dir, procs, invalidate_cache):
    if invalidate_cache and os.path.exists(sqlite_file):
        os.remove(sqlite_file)
    if os.path.exists(sqlite_file):
        print(f"loading existing database from {sqlite_file}", flush=True)
        store = MoleculeStore(sqlite_file)
    else:
        print(f"loading cached dataset from {dataset}", flush=True)
        store = CachedResultCollection.from_json(dataset).into_store(
            sqlite_file
        )

    print("started optimizing store", flush=True)
    start = time.time()
    optimize_mm(store, force_field=forcefield, n_processes=procs)
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
