from openff.qcsubmit.results import OptimizationResultCollection
from qcportal import PortalClient

client = PortalClient("https://api.qcarchive.molssi.org:443/")
dataset = OptimizationResultCollection.from_server(
    client=client,
    datasets=["OpenFF Torsion Benchmark Supplement v1.0"],
    spec_name="default",
)

with open("unfiltered-supp.json", "w") as out:
    out.write(dataset.json(indent=2))
