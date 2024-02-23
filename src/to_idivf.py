from openff.toolkit import ForceField

init = ForceField("openff-2.1.0.offxml")
h = init.get_parameter_handler("ProperTorsions")

with open("new_tm_params.dat") as inp:
    new_params = [line.strip() for line in inp]

for p in h.parameters:
    if p.id not in new_params:
        continue
    for per in range(len(p.periodicity)):
        p.idivf[per] = "experimental-auto"

init.to_file("forcefields/tm-idivf-sage-2.1.0.offxml")
