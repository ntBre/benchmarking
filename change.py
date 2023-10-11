#!/usr/bin/env python

# determine changes between starting and ending parameters for a force field

import math
from collections import defaultdict

import click
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
    match math.ceil(ll / chunk):
        case 0 | 1:
            rows, cols = 1, 1
        case 2:
            rows, cols = 2, 1
        case 3 | 4:
            rows, cols = 2, 2
        case 5 | 6:
            rows, cols = 3, 2
        case 7 | 8:
            rows, cols = 4, 2
        case 9 | 10:
            rows, cols = 5, 2
        case e:
            raise ValueError(e)

    for i in range(0, ll, chunk):
        end = min(i + chunk, ll)
        ax1 = plt.subplot(rows, cols, i // chunk + 1)
        inner(ax1, ids[i:end], lens[i:end], title)
    fig.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()


class Diff:
    def __init__(self, start, end):
        def load(ff):
            return ForceField(ff, allow_cosmetic_attributes=True)

        self.start = load(start)
        self.end = load(end)

    def check(self, param, attrs):
        hs = self.start.get_parameter_handler(param)
        he = self.end.get_parameter_handler(param)

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

    def check_bonds(self):
        vals = self.check("Bonds", ["k", "length"])
        plot(vals["k"], "Bond k", "change/bond-k.png")
        plot(vals["length"], "Bond Len", "change/bond-len.png")

    def check_angles(self):
        vals = self.check("Angles", ["k", "angle"])
        plot(vals["k"], "Angle k", "change/angle-k.png")
        plot(vals["angle"], "Angle", "change/angle.png")

    def check_torsions(self):
        vals = self.check(
            "ProperTorsions", ["k1", "k2", "k3", "k4", "k5", "k6"]
        )
        for i in range(1, 7):
            plot(vals[f"k{i}"], f"Torsion k{i}", f"change/torsion-k{i}.png")


# example usage:
# ./change.py \
# -s ../valence-fitting/04_fit-forcefield/fb-fit/forcefield/force-field.offxml\
# -e forcefields/tm.offxml
@click.command()
@click.option("--start", "-s", help="name of the initial force field")
@click.option("--end", "-e", help="name of the final force field")
def main(start, end):
    diff = Diff(start, end)
    diff.check_bonds()
    diff.check_angles()
    diff.check_torsions()


if __name__ == "__main__":
    main()
