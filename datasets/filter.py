import logging

import qcportal  # for zstd issue
from openff.interchange import Interchange
from openff.interchange.exceptions import UnassignedTorsionError
from openff.qcsubmit.results import OptimizationResultCollection
from openff.qcsubmit.results.filters import SinglepointRecordFilter
from openff.toolkit import ForceField
from openff.toolkit.utils.exceptions import (
    ChargeCalculationError,
    ConformerGenerationError,
)
from openff.toolkit.utils.toolkits import OpenEyeToolkitWrapper

logging.getLogger("openff").setLevel(logging.ERROR)


class ChargeCheckFilter(SinglepointRecordFilter):
    def _filter_function(self, result, record, molecule) -> bool:
        try:
            OpenEyeToolkitWrapper().assign_partial_charges(
                molecule, partial_charge_method="am1bccelf10"
            )
        except (ChargeCalculationError, ConformerGenerationError):
            return False
        else:
            return True


class UnassignedTorsionFilter(SinglepointRecordFilter):
    def _filter_function(self, result, record, molecule) -> bool:
        try:
            Interchange.from_smirnoff(
                ForceField("openff-2.1.0.offxml"), [molecule]
            )
        except UnassignedTorsionError:
            return False
        else:
            return True


dataset = OptimizationResultCollection.parse_file("unfiltered-supp.json")
print("before: ", dataset.n_results)
dataset = dataset.filter(ChargeCheckFilter())
print("after charge: ", dataset.n_results)
dataset = dataset.filter(UnassignedTorsionFilter())
print("after torsions: ", dataset.n_results)

with open("supp.json", "w") as out:
    out.write(dataset.json(indent=2))