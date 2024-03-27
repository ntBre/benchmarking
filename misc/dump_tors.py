from sys import argv

from openff.toolkit import ForceField

ff = ForceField(argv[1], allow_cosmetic_attributes=True)


h = ff.get_parameter_handler("Bonds")
for t in h.parameters:
    print(f"{t.id}-k,{t.k.magnitude}")
    print(f"{t.id}-length,{t.length.magnitude}")

h = ff.get_parameter_handler("Angles")
for t in h.parameters:
    print(f"{t.id}-k,{t.k.magnitude}")
    print(f"{t.id}-angle,{t.angle.magnitude}")

h = ff.get_parameter_handler("ProperTorsions")
for t in h.parameters:
    for i in range(1, 7):
        k = f"k{i}"
        p = getattr(t, k, None)
        if p is None:
            continue
        print(f"{t.id}-{k},{p.magnitude}")
