import subprocess

from main import plot


def plotter(ffs, names=None):
    if names is None:
        names = ffs
    plot("/tmp", [f"output/industry/{ff}" for ff in ffs], names)


def plot_tm():
    with open("tm.records.dat") as inp:
        records = [rec.strip() for rec in inp.readlines()]
    plot(
        "/tmp",
        [
            "output/industry/tm-tm",
            # "output/industry/tm-new",
            "output/industry/sage-tm",
            # "output/industry/sage-sage",
            # "output/industry/my-sage-2.1.0",
            # "output/industry/pavan-2.1.0",
            # "output/industry/pavan-repeat",
            # "output/industry/pavan-2.1.0-repeat",
            "output/industry/sage-2.1.0",
        ],
        names=[
            "Torsion Multiplicity Force Field and Data Set",
            # "TM-TM new",
            "Sage 2.1.0 Force Field with Torsion Multiplicity Data Set",
            # "Sage-Sage",
            # "My Sage 2.1.0",  # my environment (-oe) on sage 2.1 input files
            # "Pavan env",  # pavan's env with sage 2.1.0 input files
            # "Pavan repeat",  # pavan's env with sage 2.1.0 input files again
            # "Pavan env bench 2",  # repeated only the benchmark
            "Sage 2.1.0 Force Field and Data Set",
        ],
        filter_records=records,
        negate=True,
    )


def plot_repro():
    "Three runs of Sage 2.1.0 refit with Pavan's env and input files"
    plotter(["pavan-2.1.0", "pavan-repeat", "sage-2.1.0"])


def plot_espaloma():
    plotter(
        [
            "esp-full",
            "esp-full-refit",
            # "esp-full-full",
            "sage-2.1.0",
            # "espaloma",
        ],
        names=[
            "Espaloma bond and angle force constants",
            "Espaloma bond and angle force constants, refit",
            "Sage 2.1.0",
        ],
    )


def plot_besmarts():
    plotter(["besmarts-ba", "sage-2.1.0", "espaloma"])


def plot_msm():
    plotter(
        [
            "sage-2.1.0",
            "msm",
            "msm-split",
        ]
    )


def sage_sage():
    plotter(["sage-sage", "sage-sage-new", "my-sage-2.1.0", "sage-2.1.0"])


plot_tm()
# plot_espaloma()
# plot_besmarts()
# plot_msm()
# sage_sage()
# plot_repro()

# plotter(["my-sage-2.1.0", "pavan-2.1.0", "pavan-repeat", "sage-2.1.0"])

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
