import subprocess
from sys import argv

from main import plot


def plotter(ffs, names=None):
    if names is None:
        names = ffs
    plot("/tmp", [f"output/industry/{ff}" for ff in ffs], names)


if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: plot.py [FORCEFIELD...]")
        exit(1)
    plotter(argv[1:])
    subprocess.run(
        [
            "montage",
            "/tmp/rmsd.png",
            "/tmp/tfd.png",
            "/tmp/step_dde.png",
            # "/tmp/dde.png",
            "-geometry",
            "640x480>",
            "-tile",
            "2x2",
            "/tmp/out.png",
        ]
    )
