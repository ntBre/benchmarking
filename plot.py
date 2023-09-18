import subprocess

from main import plot


def plot_tm():
    plot(
        "/tmp",
        [
            "output/industry/tm",
            # "output/industry/sage-tm",
            # "output/industry/sage-sage",
            "output/industry/sage-2.1.0",
        ],
        names=[
            #
            "TM",
            # "Sage TM",
            # "My Sage",
            "Sage",
        ],
    )


def plot_espaloma():
    plot(
        "/tmp",
        [
            "output/industry/esp-tors-10",
            "output/industry/esp-full",
            "output/industry/sage-2.1.0",
        ],
        names=["esp-tors-10", "esp-full", "Sage"],
    )


plot_tm()
# plot_espaloma()
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
