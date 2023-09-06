from pprint import pprint

from debug import inner

eps = 10.0
tm = set(inner(eps, False, "TM"))
sage_tm = set(inner(eps, False, "Sage TM"))

print("Shared")
pprint(tm & sage_tm)

print("TM only")
pprint((tm & sage_tm) ^ tm)

print("Sage TM only")
pprint((tm & sage_tm) ^ sage_tm)
