# determine changes between starting and ending parameters for a force field

from collections import defaultdict

import matplotlib.pyplot as plt
from openff.toolkit import ForceField


def plot(ids, lens, title, filename):
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.bar(ids, lens)
    ax.set_xticklabels(ids, rotation=270)
    ax.set_title(title)
    fig.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


start = ForceField(
    "../valence-fitting/04_fit-forcefield/fb-fit/forcefield/"
    "force-field.offxml",
    allow_cosmetic_attributes=True,
)
end = ForceField("forcefields/tm.offxml", allow_cosmetic_attributes=True)


def check(param, attrs):
    hs = start.get_parameter_handler(param)
    he = end.get_parameter_handler(param)

    ids = []
    ret = defaultdict(list)
    for s in hs:
        if "parameterize" not in s._cosmetic_attribs:
            continue
        ids.append(s.id)
        e = he.get_parameter(dict(id=s.id))[0]
        for attr in attrs:
            f = getattr(e, attr, None)
            i = getattr(s, attr, None)
            if f is None or i is None:
                continue
            assert f.units == i.units
            ret[attr].append((f - i).magnitude)

    return ids, ret


def check_bonds():
    ids, vals = check("Bonds", ["k", "length"])
    plot(ids, vals["k"], "Bond k", "change/bond-k.png")
    plot(ids, vals["length"], "Bond Len", "change/bond-len.png")


def check_angles():
    ids, vals = check("Angles", ["k", "angle"])
    plot(ids, vals["k"], "Angle k", "change/angle-k.png")
    plot(ids, vals["angle"], "Angle", "change/angle.png")


def check_torsions():
    ids, vals = check("ProperTorsions", ["k1", "k2", "k3", "k4", "k5", "k6"])
    for i in range(1, 7):
        plot(ids, vals[f"k{i}"], f"Torsion k{i}", f"change/angle-k{i}.png")


if __name__ == "__main__":
    check_bonds()
    check_angles()
    # TODO fix torsion mismatch for some missing k values, probably group id
    # with the other measures
    check_torsions()
