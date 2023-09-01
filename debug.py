# more plots of data, trying to figure out why adding TM data worsens the FF
# quality

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sea

tm = pd.read_csv("output/industry/dde.csv").rename(
    columns={"difference": "TM"}
)
sage_tm = pd.read_csv("output/industry/sage/dde.csv").rename(
    columns={"difference": "Sage TM"}
)
sage_sage = pd.read_csv("output/industry/sage_sage/dde.csv").rename(
    columns={"difference": "Sage"}
)

data = tm.merge(sage_tm).merge(sage_sage)

# hilarious
data = data.drop("Unnamed: 0", axis=1)

ax = sea.histplot(
    data=data,
    binwidth=1.0,
    # kde=True,
    common_bins=True,
    element="step",
    fill=False,
)
ax.set_xlim((-15, 15))
ax.set_xlabel("dde")
plt.savefig("debug.png", dpi=200)
