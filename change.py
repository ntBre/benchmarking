# determine changes between starting and ending parameters for a force field

import matplotlib.pyplot as plt
from openff.toolkit import ForceField


def plot(ids, lens, title):
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.bar(ids, lens)
    ax.set_xticklabels(ids, rotation=270)
    ax.axhline(y=1.0, color="black", linestyle="--")
    ax.set_title(title)
    fig.tight_layout()
    plt.show()
    plt.close()


start = ForceField(
    "../valence-fitting/04_fit-forcefield/fb-fit/forcefield/"
    "force-field.offxml",
    allow_cosmetic_attributes=True,
)
end = ForceField("forcefields/tm.offxml", allow_cosmetic_attributes=True)

param = "Bonds"
hs = start.get_parameter_handler(param)
he = end.get_parameter_handler(param)

lens = []
ks = []
ids = []
for s in hs:
    if "parameterize" not in s._cosmetic_attribs:
        continue
    ids.append(s.id)
    e = he.get_parameter(dict(id=s.id))[0]
    assert e.length.units == s.length.units
    lens.append((e.length / s.length).magnitude)
    assert e.k.units == s.k.units
    ks.append((e.k / s.k).magnitude)


plot(ids, ks, "Bond k")
