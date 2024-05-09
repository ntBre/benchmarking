import json
import warnings
from collections import defaultdict
from pathlib import Path

from plot import load_csvs

warnings.simplefilter("ignore")
with warnings.catch_warnings():
    import click
    from openff.qcsubmit.results import OptimizationResultCollection
    from openff.toolkit import ForceField, Molecule
    from tqdm import tqdm


@click.command()
@click.option("--dataset", "-d", default="datasets/industry.json")
@click.option("--forcefield", "-f", default="sage-2.1.0.offxml")
@click.option("--csv_dir", "-c")
@click.option("--output", "-o", default="triage.json")
def main(dataset, forcefield, csv_dir, output):
    ds = OptimizationResultCollection.parse_file(dataset)
    data = [v for value in ds.entries.values() for v in value]

    record_ids = [int(i) for i in load_csvs(Path(csv_dir)).rec_id]

    # convert to molecules, filtering records that failed in the benchmark
    pairs = (
        (
            r.record_id,
            Molecule.from_mapped_smiles(r.cmiles, allow_undefined_stereo=True),
        )
        for r in data
        if r.record_id in record_ids
    )

    ff = ForceField(
        f"forcefields/{forcefield}", allow_cosmetic_attributes=True
    )

    # I don't strictly need to keep the list around, and that's going to use a
    # lot of memory, but then I can compute any statistics I want at the end
    errors = defaultdict(list)
    for rec_id, mol in tqdm(pairs, total=len(data), desc="Processing"):
        labels = ff.label_molecules(mol.to_topology())[0]
        for key in ["Bonds", "Angles", "ProperTorsions", "ImproperTorsions"]:
            for p in labels[key].values():
                errors[p.id].append(rec_id)

    with open(output, "w") as out:
        json.dump(errors, out, indent=2)


if __name__ == "__main__":
    main()
