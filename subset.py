# identify a minimal subset of the benchmarking data set for more rapid
# approximate benchmarks

import warnings

with warnings.catch_warnings():
    from openff.qcsubmit.results import OptimizationResultCollection
    from openff.toolkit import ForceField

ff = ForceField("openff-2.1.0.offxml")
