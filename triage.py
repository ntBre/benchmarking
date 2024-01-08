#!/usr/bin/env python

# determining average error for each parameter, adapted from hist.py

import json
import logging
from collections import defaultdict
from pathlib import Path

import click
import numpy as np
import pandas as pd
from openff.qcsubmit.results import OptimizationResultCollection
from openff.toolkit import ForceField, Molecule
from tqdm import tqdm

logging.getLogger("openff").setLevel(logging.ERROR)

# each molecule in the data set can be labeled to determine the associated
# parameters, and then we can look up the error associated with that record_id
# in the associated output file


def load_csv(forcefield):
    """Load a DDE CSV from the output directory corresponding to forcefield"""
    base = Path(forcefield).stem
    dde = pd.read_csv(f"output/industry/{base}/dde.csv")
    dde.columns = ["record", "diff"]
    return {str(r): d for r, d in zip(dde["record"], dde["diff"])}


@click.group()
def cli():
    pass


@cli.command()
@click.option("--input", "-i", default="triage.json")
def parse(input):
    with open(input, "r") as inp:
        errors = json.load(inp)

    print(f"{'param':>5} {'count':>8} {'abs mean':>12} {'std':>8}")
    for k, v in errors.items():
        print(f"{k:>5} {len(v):8} {abs(np.mean(v)):12.8f} {np.std(v):8.4f}")


@cli.command()
@click.option("--dataset", "-d", default="datasets/industry.json")
@click.option("--forcefield", "-f", default="sage-2.1.0.offxml")
@click.option("--output", "-o", default="triage.json")
def generate(dataset, forcefield, output):
    ds = OptimizationResultCollection.parse_file(dataset)
    data = [v for value in ds.entries.values() for v in value]

    dde = load_csv(forcefield)

    # convert to molecules, filtering records that failed in the benchmark
    pairs = (
        (
            r.record_id,
            Molecule.from_mapped_smiles(r.cmiles, allow_undefined_stereo=True),
        )
        for r in data
        if r.record_id in dde
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
                errors[p.id].append(dde[rec_id])

    with open(output, "w") as out:
        json.dump(errors, out, indent=2)


if __name__ == "__main__":
    cli()
