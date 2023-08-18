from multiprocessing import Pool

import click
from openff.qcsubmit.results.filters import ResultRecordFilter
from openff.qcsubmit.results.results import OptimizationResultCollection
from openff.toolkit import Molecule
from openff.toolkit.utils.exceptions import (
    ChargeCalculationError,
    ConformerGenerationError,
)
from openff.toolkit.utils.toolkits import OpenEyeToolkitWrapper
from tqdm import tqdm


# taken from valence-fitting
class ChargeCheckFilter(ResultRecordFilter):
    def _filter_function(self, _result, _record, molecule) -> bool:
        # Some of the molecules fail charging with am1bccelf10 either
        # because of no bccs or failed conformer generation, sometimes it
        # cannot be captured with just the cmiles present in the record
        # metadata, so reading from file and checking it
        can_be_charged = True
        try:
            OpenEyeToolkitWrapper().assign_partial_charges(
                molecule, partial_charge_method="am1bccelf10"
            )
        except (ChargeCalculationError, ConformerGenerationError):
            can_be_charged = False

        return can_be_charged


def filter_entry(arg):
    i, entry = arg
    filt = ChargeCheckFilter()
    molecule = Molecule.from_mapped_smiles(
        entry.cmiles, allow_undefined_stereo=True
    )
    if filt._filter_function(None, None, molecule):
        return entry
    else:
        print(f"removing entry {i}")
        return None


@click.command()
@click.option("--nprocs", default=12)
def main(nprocs):
    ds = OptimizationResultCollection.parse_file("datasets/industry.json")
    keys = ds.entries.keys()
    assert len(keys) == 1
    key = list(keys)[0]
    filtered_entries = []
    with Pool(processes=nprocs) as pool:
        for result in tqdm(
            pool.imap(filter_entry, enumerate(ds.entries[key])),
            desc="Filtering dataset",
            total=len(ds.entries[key]),
        ):
            if result:
                filtered_entries.append(result)

    ds.entries = filtered_entries
    with open("datasets/filtered-industry.json", "w") as out:
        out.write(ds.json(indent=2))


if __name__ == "__main__":
    main()
