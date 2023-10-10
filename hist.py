# associating records with parameters

import json
import logging
from collections import defaultdict

from openff.qcsubmit.results import OptimizationResultCollection
from openff.toolkit import ForceField, Molecule
from tqdm import tqdm


class Record:
    def __init__(self, bonds=None, angles=None, torsions=None):
        if bonds is None:
            bonds = defaultdict(int)
        if angles is None:
            angles = defaultdict(int)
        if torsions is None:
            torsions = defaultdict(int)
        self.bonds = bonds
        self.angles = angles
        self.torsions = torsions

    def __repr__(self):
        return (
            f"Record {{ bonds: {self.bonds}, angles: {self.angles}, "
            f"torsions: {self.torsions} }}"
        )

    def to_json(self):
        return dict(
            bonds=list(self.bonds),
            angles=list(self.angles),
            torsions=list(self.torsions),
        )

    def from_file(filename):
        "Load a sequence of `Record`s from `filename`"
        with open(filename) as inp:
            d = json.load(inp)
        ret = {}
        for rec, data in d.items():
            ret[rec] = Record(data["bonds"], data["angles"], data["torsions"])
        return ret


logging.getLogger("openff").setLevel(logging.ERROR)


def main():
    ds = OptimizationResultCollection.parse_file("datasets/industry.json")
    data = [v for value in ds.entries.values() for v in value]

    pairs = (
        (
            r.record_id,
            Molecule.from_mapped_smiles(r.cmiles, allow_undefined_stereo=True),
        )
        for r in data
    )

    ff = ForceField("forcefields/tm.offxml", allow_cosmetic_attributes=True)

    records = defaultdict(Record)
    for rec_id, mol in tqdm(pairs, total=len(data), desc="Processing"):
        labels = ff.label_molecules(mol.to_topology())[0]
        for bond in labels["Bonds"].values():
            records[rec_id].bonds[bond.id] += 1
        for angle in labels["Angles"].values():
            records[rec_id].angles[angle.id] += 1
        for torsion in labels["ProperTorsions"].values():
            records[rec_id].torsions[torsion.id] += 1

    with open("hist.json", "w") as out:
        json.dump(records, out, indent=2, default=Record.to_json)


if __name__ == "__main__":
    main()
