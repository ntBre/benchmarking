#!/usr/bin/env python

# determine changes between starting and ending parameters for a force field

import math
import os
import warnings
from collections import defaultdict

import click
import matplotlib.pyplot as plt
from openff.toolkit import ForceField

warnings.filterwarnings("ignore")


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
    def __init__(self, start, end, eps, plot, out_dir=None):
        def load(ff):
            return ForceField(ff, allow_cosmetic_attributes=True)

        self.start = load(start)
        self.end = load(end)
        self.eps = eps
        self.plot = plot
        if out_dir is None:
            out_dir = "."
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        self.out_dir = out_dir

    def check(self, param, attrs):
        hs = self.start.get_parameter_handler(param)
        he = self.end.get_parameter_handler(param)

        ret = defaultdict(list)
        for s in hs:
            e = he.get_parameter(dict(id=s.id))[0]
            for attr in attrs:
                f = getattr(e, attr, None)
                i = getattr(s, attr, None)
                if f is None or i is None:
                    continue
                i = i.to(f.units)
                assert f.units == i.units
                d = (f - i).magnitude
                if abs(d) > self.eps:
                    end = f.magnitude
                    start = i.magnitude
                    print(
                        f"{s.id:<5}{attr:<8}{start:12.4f}{end:12.4f}{d:12.4f}"
                    )
                ret[attr].append((s.id, d))

        return ret

    def check_bonds(self):
        vals = self.check("Bonds", ["k", "length"])
        if self.plot:
            plot(vals["k"], "Bond k", f"{self.out_dir}/bond-k.png")
            plot(vals["length"], "Bond Len", f"{self.out_dir}/bond-len.png")

    def check_angles(self):
        vals = self.check("Angles", ["k", "angle"])
        if self.plot:
            plot(vals["k"], "Angle k", f"{self.out_dir}/angle-k.png")
            plot(vals["angle"], "Angle", f"{self.out_dir}/angle.png")

    def check_torsions(self):
        vals = self.check(
            "ProperTorsions", ["k1", "k2", "k3", "k4", "k5", "k6"]
        )
        if self.plot:
            for i in range(1, 7):
                plot(
                    vals[f"k{i}"],
                    f"Torsion k{i}",
                    f"{self.out_dir}/torsion-k{i}.png",
                )


# example usage:
# ./change.py \
# -s ../valence-fitting/04_fit-forcefield/fb-fit/forcefield/force-field.offxml\
# -e forcefields/tm.offxml
@click.command()
@click.option("--start", "-s", help="name of the initial force field")
@click.option("--end", "-e", help="name of the final force field")
@click.option("--out-dir", "-o", help="where to write plots", default=None)
@click.option("--eps", help="threshold for printing differences", default=0.0)
@click.option("--plot", "-p", is_flag=True, default=False)
def main(start, end, eps, plot, out_dir):
    diff = Diff(start, end, eps, plot, out_dir)
    diff.check_bonds()
    diff.check_angles()
    diff.check_torsions()


if __name__ == "__main__":
    main()
