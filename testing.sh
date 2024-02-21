function get_tiny() {
	python cache_dataset.py -d datasets/tiny-opt.json \
							-o datasets/cache/tiny-opt.json
}

set -xe

python main.py	-f forcefields/sage-2.1.0.offxml \
				-d datasets/cache/tiny-opt.json \
				-s tmp.sqlite \
				-p 8 \
				--invalidate-cache

# check the maximum deviation across runs, normal values seem to be around 0,
# 0.5, and 1.3, respectively
./csvdiff.R dde.csv true/dde.csv
./csvdiff.R tfd.csv true/tfd.csv
./csvdiff.R rmsd.csv true/rmsd.csv

rm dde.csv dde.png rmsd.csv rmsd.png step_dde.png tfd.csv tfd.png
