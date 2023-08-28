from main import plot

# "TM" is the Sage 2.1.0 force field with the torsion multiplicity changes,
# trained on the tm dataset
#
# "Sage TM" is the original Sage 2.1.0 force field trained on the tm dataset
#
# "Sage" is the original Sage 2.1.0 force field trained on the original dataset

plot(
    "/tmp",
    ["output/industry/", "output/industry/sage"],
    names=["TM", "Sage TM"],
)
