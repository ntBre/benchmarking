# printing the differences from debug as sets and seeing how they overlap

from pprint import pprint

from debug import inner


def display(label, s):
    print(f"{label} = {len(s)}")
    pprint(s)


eps = 5.0
tm = set(inner(eps, False, "TM"))
sage_tm = set(inner(eps, False, "Sage TM"))

display("Shared", tm & sage_tm)
display("TM only", (tm & sage_tm) ^ tm)
display("Sage TM only", (tm & sage_tm) ^ sage_tm)
