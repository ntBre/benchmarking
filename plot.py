from pathlib import Path

import click
import numpy as np
import pandas as pd

from main import plot

pd.set_option("display.max_columns", None)


def load_csvs(dir: Path):
    """Load the DDE, RMSD, and TFD CSV files in `dir` and return the merged
    dataframe"""
    dde = pd.read_csv(dir / "dde.csv")
    dde.columns = ["rec_id", "dde"]
    rmsd = pd.read_csv(dir / "rmsd.csv")
    rmsd.columns = ["rec_id", "rmsd"]
    tfd = pd.read_csv(dir / "tfd.csv")
    tfd.columns = ["rec_id", "tfd"]
    return dde.merge(rmsd).pipe(pd.DataFrame.merge, tfd)


def stats(dirs, out):
    res = []
    for d in dirs:
        d = Path(d)
        df = load_csvs(d)
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


def plotter(ffs, output_dir, input_dir="industry", names=None, **kwargs):
    if names is None:
        names = ffs
    dirs = [f"output/{input_dir}/{ff}" for ff in ffs]
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)
    plot(output_dir, dirs, names, **kwargs)
    with open("current/tabs/stats.tex", "w") as out:
        stats(dirs, out)


@click.command()
@click.argument("forcefields", nargs=-1)
@click.option("--input-dir", "-d", default="industry")
@click.option("--filter-records", "-r", default=None)
@click.option("--negate", "-n", is_flag=True, default=False)
@click.option("--output_dir", "-o", default="current/figs")
def main(forcefields, input_dir, filter_records, negate, output_dir):
    if filter_records is not None:
        # assume it's the name of a file
        with open(filter_records) as inp:
            filter_records = [line.strip() for line in inp]
    plotter(
        forcefields,
        output_dir,
        input_dir=input_dir,
        filter_records=filter_records,
        negate=negate,
    )


if __name__ == "__main__":
    main()
