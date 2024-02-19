import json
from dataclasses import dataclass

import numpy
from ibstore import MoleculeStore
from ibstore.models import MoleculeRecord, QMConformerRecord
from openff.qcsubmit.results import OptimizationResultCollection
from openff.units import unit


@dataclass
class CachedResult:
    """All of the fields necessary to emulate
    MoleculeStore.from_qcsubmit_collection without calling
    OptimizationResultCollection.to_records

    """

    mapped_smiles: str
    inchi_key: str
    coordinates: numpy.ndarray
    qc_record_id: int
    qc_record_final_energy: float

    def to_dict(self):
        assert self.coordinates.units == unit.angstrom
        return dict(
            mapped_smiles=self.mapped_smiles,
            inchi_key=self.inchi_key,
            # this is a pint.Quantity-wrapped numpy array
            coordinates=self.coordinates.magnitude.tolist(),
            qc_record_id=self.qc_record_id,
            qc_record_final_energy=self.qc_record_final_energy,
        )


class CachedResultCollection:
    inner: list[CachedResult]

    def __init__(self):
        self.inner = []

    @classmethod
    def from_qcsubmit_collection(
        cls, collection: OptimizationResultCollection
    ):
        import qcelemental
        from tqdm import tqdm

        hartree2kcalmol = qcelemental.constants.hartree2kcalmol

        ret = cls()
        for qcarchive_record, molecule in tqdm(
            collection.to_records(),
            desc="Converting records to molecules",
        ):
            ret.inner.append(
                CachedResult(
                    mapped_smiles=molecule.to_smiles(
                        mapped=True, isomeric=True
                    ),
                    inchi_key=molecule.to_inchi(fixed_hydrogens=True),
                    coordinates=molecule.conformers[0],
                    qc_record_id=qcarchive_record.id,
                    qc_record_final_energy=qcarchive_record.get_final_energy()
                    * hartree2kcalmol,
                )
            )
        return ret

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.inner, default=CachedResult.to_dict, **kwargs)

    @classmethod
    def from_json(cls, filename):
        """Load a `CachedResultCollection` from `filename`"""
        with open(filename) as inp:
            data = json.load(inp)

        ret = cls()
        for entry in data:
            ret.inner.append(
                CachedResult(
                    mapped_smiles=entry["mapped_smiles"],
                    inchi_key=entry["inchi_key"],
                    coordinates=numpy.array(entry["coordinates"])
                    * unit.angstrom,
                    qc_record_id=entry["qc_record_id"],
                    qc_record_final_energy=entry["qc_record_final_energy"]
                    * unit.kilocalorie_per_mole,
                )
            )
        return ret

    def into_store(self, database_name) -> MoleculeStore:
        """modeled on MoleculeStore.from_qcsubmit_collection"""
        store = MoleculeStore(database_name)
        for record in self.inner:
            # adapted from MoleculeRecord.from_molecule
            molecule_record = MoleculeRecord(
                mapped_smiles=record.mapped_smiles, inchi_key=record.inchi_key
            )
            store.store(molecule_record)
            # adapted from QMConformerRecord.from_qcarchive_record
            molecule_id = store.get_molecule_id_by_smiles(
                molecule_record.mapped_smiles
            )
            store.store_qcarchive(
                QMConformerRecord(
                    molecule_id=molecule_id,
                    qcarchive_id=record.qc_record_id,
                    mapped_smiles=molecule_record.mapped_smiles,
                    coordinates=record.coordinates,
                    energy=record.qc_record_final_energy,
                )
            )
        return store
