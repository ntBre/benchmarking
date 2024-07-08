# changes in parameters

import sys

from openff.toolkit import ForceField
from openff.units import unit


class Bonds:
    name = "Bonds"

    @classmethod
    def fields(_cls):
        return [
            ("length", unit.angstrom),
            ("k", unit.kcal / unit.mole / unit.angstrom**2),
        ]


class Angles:
    name = "Angles"

    @classmethod
    def fields(_cls):
        return [
            ("angle", unit.degree),
            ("k", unit.kcal / unit.mole / unit.radians**2),
        ]


class ProperTorsions:
    name = "ProperTorsions"

    @classmethod
    def fields(_cls):
        return [("k", unit.kcal / unit.mole)]


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
        for field, units in ptype.fields():
            f = getattr(p, field)
            if isinstance(f, list):
                for i, (v1, v2) in enumerate(zip(f, getattr(q, field))):
                    v1 = v1.to(units).magnitude
                    v2 = v2.to(units).magnitude
                    fl = f"{field}{i+1}"
                    print(
                        f"{p.id:>{lw}} {fl:>{lw}.3}"
                        f" {v1:{fw}.{fp}f} {v2:{fw}.{fp}f} {v2-v1:{fw}.{fp}f}"
                    )
            else:
                v1 = getattr(p, field).to(units).magnitude
                v2 = getattr(q, field).to(units).magnitude
                print(
                    f"{p.id:>{lw}} {field:>{lw}.3}"
                    f" {v1:{fw}.{fp}f} {v2:{fw}.{fp}f} {v2-v1:{fw}.{fp}f}"
                )
