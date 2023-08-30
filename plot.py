import subprocess

from main import plot

# "TM" is the Sage 2.1.0 force field with the torsion multiplicity changes,
# trained on the tm dataset
#
# "Sage TM" is the original Sage 2.1.0 force field trained on the tm dataset
#
# "Sage" is the original Sage 2.1.0 force field trained on the original dataset

plot(
    "/tmp",
    ["output/industry/", "output/industry/sage", "output/industry/sage_sage"],
    names=["TM", "Sage TM", "Sage"],
)


subprocess.run(
    [
        "montage",
        "/tmp/rmsd.png",
        "/tmp/tfd.png",
        "/tmp/step_dde.png",
        "/tmp/dde.png",
        "-geometry",
        "640x480>",
        "-tile",
        "2x2",
        "/tmp/out.png",
    ]
)
