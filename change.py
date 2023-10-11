# determine changes between starting and ending parameters for a force field

from collections import defaultdict

import matplotlib.pyplot as plt
from openff.toolkit import ForceField


def inner(ax, ids, lens, title):
    ax.bar(ids, lens)
    ax.set_xticklabels(ids, rotation=270)
    ax.set_title(title)


def plot(lens, title, filename):
    fig, ax = plt.subplots(figsize=(12, 12))
    ids, lens = zip(*lens)
    chunk = 20
    ll = len(lens)
    for i in range(0, ll, chunk):
        end = min(i + chunk, ll)
        ax1 = plt.subplot(5, 2, i // chunk + 1)
        inner(ax1, ids[i:end], lens[i:end], title)
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

    ret = defaultdict(list)
    for s in hs:
        if "parameterize" not in s._cosmetic_attribs:
            continue
        e = he.get_parameter(dict(id=s.id))[0]
        for attr in attrs:
            f = getattr(e, attr, None)
            i = getattr(s, attr, None)
            if f is None or i is None:
                continue
            assert f.units == i.units
            ret[attr].append((s.id, (f - i).magnitude))

    return ret


def check_bonds():
    vals = check("Bonds", ["k", "length"])
    plot(vals["k"], "Bond k", "change/bond-k.png")
    plot(vals["length"], "Bond Len", "change/bond-len.png")


def check_angles():
    vals = check("Angles", ["k", "angle"])
    plot(vals["k"], "Angle k", "change/angle-k.png")
    plot(vals["angle"], "Angle", "change/angle.png")


def check_torsions():
    vals = check("ProperTorsions", ["k1", "k2", "k3", "k4", "k5", "k6"])
    for i in range(1, 7):
        plot(vals[f"k{i}"], f"Torsion k{i}", f"change/torsion-k{i}.png")


if __name__ == "__main__":
    check_bonds()
    check_angles()
    check_torsions()
