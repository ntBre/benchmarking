from ibstore import MoleculeStore

from main import get_dde

print("initializing store")

forcefield = "forcefields/cached-sage-2.1.0.offxml"
store = MoleculeStore("cached-sage-2.1.0.sqlite")

get_dde(store, forcefield)
