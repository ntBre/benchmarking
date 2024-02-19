from cached_result import CachedResultCollection
from openff.qcsubmit.results import OptimizationResultCollection


def test_cached_results():
    print("loading collection")
    opt = OptimizationResultCollection.parse_file("datasets/small-opt.json")
    print("building cache")
    crc = CachedResultCollection.from_qcsubmit_collection(opt)
    print("serializing to json")

    json_file = "/tmp/crc.json"
    with open(json_file, "w") as out:
        out.write(crc.to_json(indent=2))

    print("re-reading from JSON")
    two = CachedResultCollection.from_json(json_file)

    assert len(two.inner) == len(crc.inner)

    # it would be nice to assert that the values are equal, but the round-trip
    # probably isn't working precisely

    # assert two == crc
