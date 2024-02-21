import json
from dataclasses import dataclass

import numpy
from ibstore import MoleculeStore
from ibstore._db import DBMoleculeRecord
from ibstore.models import MoleculeRecord, QMConformerRecord
from openff.qcsubmit.results import OptimizationResultCollection
from openff.units import unit
from tqdm import tqdm


def get_molecule_id_by_smiles(db) -> dict[str, int]:
    "Return a map of MoleculeRecord mapped SMILES to MoleculeRecord ids"
    # for some reason this has to be reversed, meaning the first record
    # encountered has to win out. this matches the behavior of the original
    # version, where the query was run each time and the first result was
    # returned
    return {
        smi: id
        for id, smi in reversed(
            db.db.query(
                DBMoleculeRecord.id, DBMoleculeRecord.mapped_smiles
            ).all()
        )
    }


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
                    qc_record_final_energy=entry["qc_record_final_energy"],
                )
            )
        return ret

    def into_store(self, database_name) -> MoleculeStore:
        """modeled on MoleculeStore.from_qcsubmit_collection"""
        store = MoleculeStore(database_name)

        # adapted from MoleculeRecord.from_molecule and MoleculeStore.store
        for record in tqdm(self.inner, desc="Storing molecules"):
            store.store(
                MoleculeRecord(
                    mapped_smiles=record.mapped_smiles,
                    inchi_key=record.inchi_key,
                )
            )

        # adapted from QMConformerRecord.from_qcarchive_record and
        # MoleculeStore.store_qcarchive

        # using a simple set instead of db query each time
        # (DBSessionManager._qm_conformer_already_exists), which appears to
        # query the entire database every single time. This should work as long
        # as the store is initially empty here and it only gets updated at the
        # same time as seen. to be more rigorous, we could probably initialize
        # the set from a db query and then update it like a normal set after.
        # in practice, this is never actually used here because all of the
        # record_ids are unique
        seen = set()
        with store._get_session() as db:
            smiles_to_id = get_molecule_id_by_smiles(db)
            for record in tqdm(self.inner, desc="Storing Records"):
                if record.qc_record_id in seen:
                    continue
                seen.add(record.qc_record_id)
                mol_id = smiles_to_id[record.mapped_smiles]
                db.store_qm_conformer_record(
                    QMConformerRecord(
                        molecule_id=mol_id,
                        qcarchive_id=record.qc_record_id,
                        mapped_smiles=record.mapped_smiles,
                        coordinates=record.coordinates,
                        energy=record.qc_record_final_energy,
                    )
                )

        return store
