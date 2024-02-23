# take an existing, filled MoleculeStore and compute the desired statistics as
# at the end of main.py

import os

from ibstore import MoleculeStore

from main import make_csvs

print("initializing store")

forcefield = "forcefields/cached-sage-2.1.0.offxml"
store = MoleculeStore("cached-sage-2.1.0.sqlite")
out_dir = "output/industry/cached-sage-2.1.0"

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

make_csvs(store, forcefield, out_dir)
