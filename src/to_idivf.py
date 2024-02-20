from openff.toolkit import ForceField

init = ForceField("openff-2.1.0.offxml")
h = init.get_parameter_handler("ProperTorsions")

for p in h.parameters:
    for per in range(len(p.periodicity)):
        p.idivf[per] = "experimental-auto"

init.to_file("idivf-sage-2.1.0.offxml")
