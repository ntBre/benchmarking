import json

from openff.toolkit import ForceField

sage = ForceField("forcefields/sage-2.2.0.offxml")
sage = {p.id for p in sage.get_parameter_handler("ProperTorsions").parameters}

utm = ForceField("forcefields/ultra-tm-2.2.offxml")
utm = {p.id for p in utm.get_parameter_handler("ProperTorsions").parameters}

with open("filters/ultra-tm.json") as inp:
    d = json.load(inp)

recs = set()
for pid in utm - sage:
    if pid in d:
        recs.update(d[pid])

with open("ultra-tm.dat", "w") as out:
    for rec in recs:
        print(rec, file=out)
