import csv
import re
from collections import defaultdict

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


LABEL = re.compile(r"([bat])(\d+)([a-z]*)")


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
        print(f"{key:<5}{avg:12.4f}{std:12.4f}")
    print()


records = Record.from_file("hist.json")

tm = read_csv("output/industry/tm/dde.csv")

# these are dicts of parameter_id -> error, where error is a list of all errors
# for molecules containing these ids
bonds = defaultdict(list)
angles = defaultdict(list)
torsions = defaultdict(list)

for rec, diff in tqdm(tm.items(), desc="Parsing hist", total=len(tm)):
    rec = records[rec]
    for bond in rec.bonds:
        bonds[bond].append(diff)
    for angle in rec.angles:
        angles[angle].append(diff)
    for torsion in rec.torsions:
        torsions[torsion].append(diff)

summary(bonds, "Bonds")
summary(angles, "Angles")
summary(torsions, "Torsions")
