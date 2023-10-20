import subprocess

from main import plot


def plot_tm():
    plot(
        "/tmp",
        [
            # "output/industry/tm",
            # "output/industry/sage-tm",
            "output/industry/sage-sage",
            "output/industry/my-sage-2.1.0",
            "output/industry/pavan-2.1.0",
            "output/industry/sage-2.1.0",
        ],
        names=[
            # "TM-TM",
            # "Sage-TM",
            "Sage-Sage",
            "My Sage 2.1.0",  # my environment (-oe) on sage 2.1.0 input files
            "Pavan env",  # pavan's env with sage 2.1.0 input files
            "Sage",
        ],
    )


def plot_espaloma():
    plot(
        "/tmp",
        [
            # "output/industry/esp-tors-10",
            "output/industry/esp-full",
            "output/industry/sage-2.1.0",
            "output/industry/espaloma",
        ],
        names=[
            #
            # "esp-tors-10",
            "esp-full",
            "Sage",
            "Espaloma",
        ],
    )


def plot_besmarts():
    plot(
        "/tmp",
        [
            "output/industry/besmarts-ba",
            "output/industry/sage-2.1.0",
            "output/industry/espaloma",
        ],
        names=[
            #
            "besmarts ba",
            "Sage",
            "Espaloma",
        ],
    )


plot_tm()
# plot_espaloma()
# plot_besmarts()
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
