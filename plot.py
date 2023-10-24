import subprocess

from main import plot


def plotter(ffs, names=None):
    if names is None:
        names = ffs
    plot("/tmp", [f"output/industry/{ff}" for ff in ffs], names)


def plot_tm():
    plot(
        "/tmp",
        [
            # "output/industry/tm",
            # "output/industry/sage-tm",
            # "output/industry/sage-sage",
            # "output/industry/my-sage-2.1.0",
            "output/industry/pavan-2.1.0",
            "output/industry/pavan-repeat",
            # "output/industry/pavan-2.1.0-repeat",
            "output/industry/sage-2.1.0",
        ],
        names=[
            # "TM-TM",
            # "Sage-TM",
            # "Sage-Sage",
            # "My Sage 2.1.0",  # my environment (-oe) on sage 2.1 input files
            "Pavan env",  # pavan's env with sage 2.1.0 input files
            "Pavan repeat",  # pavan's env with sage 2.1.0 input files again
            # "Pavan env bench 2",  # repeated only the benchmark
            "Sage",
        ],
    )


def plot_espaloma():
    plotter(["esp-full", "sage-2.1.0", "espaloma"])


def plot_besmarts():
    plotter(["besmarts-ba", "sage-2.1.0", "espaloma"])


def plot_msm():
    plotter(["sage-2.1.0", "msm"])


def sage_sage():
    plotter(["sage-sage", "sage-sage-new", "my-sage-2.1.0", "sage-2.1.0"])


plot_tm()
# plot_espaloma()
# plot_besmarts()
# plot_msm()
# sage_sage()

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
