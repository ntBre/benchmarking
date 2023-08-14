# datasets/full-opt.json

csvs := dde.csv rmsd.csv tfd.csv
pngs := $(subst .csv,.png,$(csvs))

vf_training := ../valence-fitting/02_curate-data/datasets/filtered-opt.json

ensure_datasets := mkdir -p datasets

.DELETE_ON_ERROR = tmp.sqlite

output/out.png: $(addprefix output/,$(pngs))
	montage $^ -geometry 640x480\>+3+1 $@

$(addprefix output/,$(csvs) $(pngs)) status tmp.sqlite: datasets/full-opt.json main.py
	python main.py --dataset $<
	echo benchmarked $< > status

datasets/full-opt.json datasets/full-opt.sdf: sage/01-setup.py
	$(ensure_datasets)
	@echo downloading full optimization benchmark
	python $< "OpenFF Full Optimization Benchmark 1"	\
		--output datasets/full-opt

datasets/industry.json datasets/industry.sdf: sage/01-setup.py
	$(ensure_datasets)
	@echo downloading industry benchmark
	python $< "OpenFF Industry Benchmark Season 1 v1.0"	\
		--output datasets/industry
