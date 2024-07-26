# plot a single torsion (pid in argv[1]) from all force fields provided

import math
import sys

import matplotlib.pyplot as plt
import numpy as np
from openff.toolkit import ForceField


def eval_torsion(p):
    k, per, phase = p.k, p.periodicity, p.phase

    def f(phi):
        tot = 0
        for i in range(len(k)):
            tot += k[i] * (1 + math.cos(per[i] * phi - phase[i]))
        return tot.magnitude

    return f


pid = sys.argv[1]
ffnames = [f for f in sys.argv[2:]]
ffs = [ForceField(f) for f in sys.argv[2:]]

xs = np.linspace(0, 2 * math.pi, num=100)

ys = []
for ffname, ff in zip(ffnames, ffs):
    h = ff.get_parameter_handler("ProperTorsions")
    p = h.get_parameter(dict(id=pid))[0]
    f = eval_torsion(p)
    y = [f(x) for x in xs]
    ys.append(y)
    plt.plot(np.degrees(xs), y, label=ffname)

plt.title(pid)
plt.xlabel("θ (deg)")
plt.ylabel("E (kcal/mol)")
plt.legend(loc="upper right")
plt.savefig("sage-v-smee-2.1.png")
