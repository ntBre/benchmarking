# datasets/full-opt.json

csvs := dde.csv rmsd.csv tfd.csv
pngs := $(subst .csv,.png,$(csvs))
vf_training := ../valence-fitting/02_curate-data/datasets/filtered-opt.json

$(csvs) $(pngs): main.py
	python main.py --dataset $(vf_training)
