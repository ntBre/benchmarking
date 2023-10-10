# attributing errors to each parameter

import json
import logging
from collections import defaultdict

import pandas as pd
from openff.qcsubmit.results import OptimizationResultCollection
from openff.toolkit import ForceField, Molecule
from tqdm import tqdm


class Record:
    def __init__(self):
        self.bonds = set()
        self.angles = set()
        self.torsions = set()

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


logging.getLogger("openff").setLevel(logging.ERROR)

tm = pd.read_csv("output/industry/tm/dde.csv").rename(
    columns={"difference": "TM", "Unnamed: 0": "Record ID"}
)

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
        records[rec_id].bonds.add(bond.id)
    for angle in labels["Angles"].values():
        records[rec_id].angles.add(angle.id)
    for torsion in labels["ProperTorsions"].values():
        records[rec_id].torsions.add(torsion.id)

with open("hist.json", "w") as out:
    json.dump(records, out, indent=2, default=Record.to_json)
