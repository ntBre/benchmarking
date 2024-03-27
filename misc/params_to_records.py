# reads a sequence of parameter ids from a file and prints a list of record ids
# from the input data set matching these parameters

import click
from openff.qcsubmit.results import OptimizationResultCollection
from openff.toolkit import ForceField, Molecule
from tqdm import tqdm


def load_parameters(filename):
    with open(filename, "r") as inp:
        return inp.readlines()


@click.command()
@click.option("--dataset", "-d", default="datasets/industry.json")
@click.option("--forcefield", "-f", default="forcefields/tm-tm.offxml")
@click.option(
    "--parameters", "-p", default="../valence-fitting/new_params.dat"
)
def main(dataset, forcefield, parameters):
    parameters = load_parameters(parameters)
    ds = OptimizationResultCollection.parse_file(dataset)
    data = [v for value in ds.entries.values() for v in value]

    pairs = (
        (
            r.record_id,
            Molecule.from_mapped_smiles(r.cmiles, allow_undefined_stereo=True),
        )
        for r in data
    )

    ff = ForceField(forcefield, allow_cosmetic_attributes=True)

    seen = set()
    records = set()
    for rec_id, mol in tqdm(pairs, total=len(data), desc="Processing"):
        key = mol.to_inchikey()
        if key in seen:
            records.add(rec_id)
            continue
        seen.add(key)
        labels = ff.label_molecules(mol.to_topology())[0]
        for ptype in ["Bonds", "Angles", "ProperTorsions"]:
            for p in labels[ptype].values():
                if p.id in parameters:
                    records.add(rec_id)
                    break  # idiomatic break 'outer??
            else:
                continue
            break

    for r in records:
        print(r)


if __name__ == "__main__":
    main()
