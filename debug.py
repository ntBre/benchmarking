# more plots of data, trying to figure out why adding TM data worsens the FF
# quality

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sea
from openff.qcsubmit.results import OptimizationResultCollection
from openff.toolkit import Molecule
from rdkit.Chem.Draw import rdDepictor, rdMolDraw2D
from rdkit.Chem.rdmolops import RemoveHs
from tqdm import tqdm


# adapted from known-issues before the highlight stuff
def draw_rdkit(mol: Molecule, filename, show_all_hydrogens=True):
    rdmol = mol.to_rdkit()
    if not show_all_hydrogens:
        rdmol = RemoveHs(rdmol, updateExplicitCount=True)
    rdDepictor.SetPreferCoordGen(True)
    rdDepictor.Compute2DCoords(rdmol)
    rdmol = rdMolDraw2D.PrepareMolForDrawing(rdmol)

    drawer = rdMolDraw2D.MolDraw2DCairo(300, 300)
    drawer.DrawMolecule(rdmol)
    drawer.FinishDrawing()

    drawer.WriteDrawingText(filename)


def plot(data, filename="debug.png", dpi=200):
    "Plot `data` as a histplot and save the result to `filename`"

    # drop this so we don't start counting it
    data = data.drop("Record ID", axis=1)
    ax = sea.histplot(
        data=data,
        binwidth=1.0,
        # kde=True,
        common_bins=True,
        element="step",
        fill=False,
    )
    ax.set_xlim((-15, 15))
    ax.set_xlabel("dde")
    plt.savefig(filename, dpi=dpi)


tm = pd.read_csv("output/industry/dde.csv").rename(
    columns={"difference": "TM"}
)
sage_tm = pd.read_csv("output/industry/sage/dde.csv").rename(
    columns={"difference": "Sage TM"}
)
sage_sage = pd.read_csv("output/industry/sage_sage/dde.csv").rename(
    columns={"difference": "Sage"}
)

data = tm.merge(sage_tm).merge(sage_sage)

# hilarious
data = data.rename(columns={"Unnamed: 0": "Record ID"})

# list of records with substantial disagreements - 63 of these for eps = 10.0
eps = 50.0
diffs = data[abs(data["Sage TM"] - data["Sage"]) > eps]

# some of these are actually better in Sage TM, so filter further by the ones
# with larger magnitudes in the TM version - 36 for eps = 10.0
our_bad = diffs[abs(diffs["Sage TM"]) > abs(diffs["Sage"])]
print(our_bad)

records = list(our_bad["Record ID"])
print(records)

ds = OptimizationResultCollection.parse_file("datasets/industry.json")
data = [v for value in ds.entries.values() for v in value]

data = [rec for rec in data if int(rec.record_id) in records]

molecules = [
    Molecule.from_mapped_smiles(r.cmiles, allow_undefined_stereo=True)
    for r in tqdm(data, desc="Converting to molecules")
]

for i, mol in enumerate(molecules):
    draw_rdkit(mol, f"debug/mol{i}.png")
