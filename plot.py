from pathlib import Path
from sys import argv

import click
import numpy as np
import pandas as pd

from main import plot

pd.set_option("display.max_columns", None)


def stats(dirs, out):
    res = []
    for d in dirs:
        d = Path(d)
        dde = pd.read_csv(d / "dde.csv")
        dde.columns = ["rec_id", "dde"]
        rmsd = pd.read_csv(d / "rmsd.csv")
        rmsd.columns = ["rec_id", "rmsd"]
        tfd = pd.read_csv(d / "tfd.csv")
        tfd.columns = ["rec_id", "tfd"]
        df = dde.merge(rmsd).pipe(pd.DataFrame.merge, tfd)
        res.append((d.name, df))

    for m in ["dde", "rmsd", "tfd"]:
        for n, df in res:
            data = df[df[m].notnull()][m]
            avg = np.mean(data)
            mae = np.mean(np.abs(data))
            mdn = np.median(data)
            std = np.std(data)
            o = m.upper()
            print(
                f"{n}&{o}& {avg:.2f} & {mae:.2f} & {mdn:.2f} & {std:.2f} \\\\",
                file=out,
            )
        print("\\hline", file=out)


def plotter(ffs, dir="industry", names=None, **kwargs):
    if names is None:
        names = ffs
    dirs = [f"output/{dir}/{ff}" for ff in ffs]
    plot("current/figs", dirs, names, **kwargs)
    with open("current/tabs/stats.tex", "w") as out:
        stats(dirs, out)


@click.command()
@click.argument("forcefields", nargs=-1)
@click.option("--dir", "-d", default="industry")
@click.option("--filter-records", "-r", default=None)
@click.option("--negate", "-n", is_flag=True, default=False)
def main(forcefields, dir, filter_records, negate):
    plotter(forcefields, dir=dir, filter_records=filter_records, negate=negate)


if __name__ == "__main__":
    main()
