full-opt.json full-opt.sdf: 01-setup.py
	python $^ "OpenFF Full Optimization Benchmark 1" --output full-opt

industry.json industry.sdf: 01-setup.py
	python $^ "OpenFF Industry Benchmark Season 1 v1.0" --output industry

output.sdf: 02-b-minimize.py full-opt.sdf
	python 02-b-minimize.py			\
		--input-sdf full-opt.sdf	\
		--force-field forcefield.offxml \
		--output $@
