# changes in parameters

import sys

from openff.toolkit import ForceField


class Bonds:
    name = "Bonds"

    @classmethod
    def fields(_cls):
        return ["length", "k"]


class Angles:
    name = "Angles"

    @classmethod
    def fields(_cls):
        return ["angle", "k"]


class ProperTorsions:
    name = "ProperTorsions"

    @classmethod
    def fields(_cls):
        return ["k"]


ff1 = ForceField(sys.argv[1])
ff2 = ForceField(sys.argv[2])

lw = 5  # label width
fw = 7  # field width
fp = 2  # field precision
print(f"{'pid':>{lw}} {'typ':>{lw}} {'v1':>{fw}} {'v2':>{fw}} {'Δ':>{fw}}")
for ptype in [Bonds, Angles, ProperTorsions]:
    g = ff1.get_parameter_handler(ptype.name)
    h = ff2.get_parameter_handler(ptype.name)
    for p, q in zip(g.parameters, h.parameters):
        assert p.id == q.id
        for field in ptype.fields():
            f = getattr(p, field)
            if isinstance(f, list):
                for i, (v1, v2) in enumerate(zip(f, getattr(q, field))):
                    v1 = v1.magnitude
                    v2 = v2.magnitude
                    fl = f"{field}{i+1}"
                    print(
                        f"{p.id:>{lw}} {fl:>{lw}.3}"
                        f" {v1:{fw}.{fp}f} {v2:{fw}.{fp}f} {v2-v1:{fw}.{fp}f}"
                    )
            else:
                v1 = getattr(p, field).magnitude
                v2 = getattr(q, field).magnitude
                print(
                    f"{p.id:>{lw}} {field:>{lw}.3}"
                    f" {v1:{fw}.{fp}f} {v2:{fw}.{fp}f} {v2-v1:{fw}.{fp}f}"
                )
