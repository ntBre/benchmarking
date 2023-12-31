import csv
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from hist import Record


def read_csv(filename):
    "Read a CSV and return a dict of record_id: error pairs"
    ret = {}
    with open(filename, newline="") as inp:
        header = inp.readline()  # skip header
        assert "difference" in header
        inp = csv.reader(inp)  # probably not necessary for such a simple file
        for line in inp:
            assert len(line) == 2
            ret[line[0]] = float(line[1])
    return ret


LABEL = re.compile(r"([bati])(\d+)([a-z]*)")


def sort_label(key):
    t, n, tail = LABEL.match(key).groups()
    return (t, int(n), tail)


def summary(items, label):
    print(f"== {label} ==")
    keys = sorted(items.keys(), key=sort_label)
    for key in keys:
        vals = items[key]
        avg = np.average(vals)
        std = np.std(vals)
        min = np.min(vals)
        max = np.max(vals)
        print(f"{key:<5}{avg:12.4f}{std:12.4f}{min:12.4f}{max:12.4f}")
    print()


def plot(params, filename):
    keys = sorted(params.keys(), key=sort_label)
    nkeys = len(keys)
    vals = [params[k] for k in keys]
    bsize = 40
    for i in range(0, nkeys, bsize):
        fig, ax = plt.subplots()
        end = min(i + bsize, nkeys)
        bp = ax.boxplot(
            vals[i:end],
            # whis=(0, 100),
            flierprops={
                "marker": "o",
                "markersize": 1,
                "markerfacecolor": "black",
            },
        )
        for m in bp["medians"]:
            m.set_color("blue")
        ax.set_xticklabels(keys[i:end], rotation=270)
        # ax.set_ylim(-8, 12)
        plt.xlabel("Parameter")
        plt.ylabel("DDE (kcal mol$^{-1}$)")
        # ax.set_title("Errors by parameter (whiskers are range)")
        ax.set_title("Errors by parameter")
        plt.tight_layout()
        plt.savefig(filename.format(i), dpi=300)
        plt.close()


def main():
    records = Record.from_file("hist.json")

    tm = read_csv("output/industry/tm/dde.csv")

    # these are dicts of parameter_id -> error, where error is a list of all
    # errors for molecules containing these ids
    bonds = defaultdict(list)
    angles = defaultdict(list)
    torsions = defaultdict(list)

    for rec, diff in tqdm(tm.items(), desc="Parsing hist", total=len(tm)):
        rec = records[rec]
        for bond, count in rec.bonds.items():
            bonds[bond].extend([diff] * count)
        for angle, count in rec.angles.items():
            angles[angle].extend([diff] * count)
        for torsion, count in rec.torsions.items():
            torsions[torsion].extend([diff] * count)

    for name in ["bonds", "angles", "torsions"]:
        # summary(locals()[name], name.title())
        plot(locals()[name], "hist/" + name + "{:03d}.png")


if __name__ == "__main__":
    main()
