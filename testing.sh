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
Rscript csvdiff.R dde.csv true/dde.csv
Rscript csvdiff.R tfd.csv true/tfd.csv
Rscript csvdiff.R rmsd.csv true/rmsd.csv