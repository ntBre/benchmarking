# datasets/full-opt.json

csvs := dde.csv rmsd.csv tfd.csv
pngs := $(subst .csv,.png,$(csvs))

# for specifying a subdirectory of output. the name must match the filename of
# an existing force field .offxml file in FF_DIR
TARGET =

FF_DIR = forcefields

forcefield = force-field.offxml
ifdef TARGET
    forcefield = $(FF_DIR)/$(TARGET).offxml
endif

$(addprefix output/%/$(TARGET)/,$(csvs) $(pngs)) %.sqlite: datasets/%.json main.py $(forcefield)
# DO NOT run M-x align here, it adds spaces around the bash =
	base=$(basename $(notdir $<));					\
	mkdir -p output/$$base/$(TARGET);				\
	python main.py --dataset $< --sqlite-file $$base.$(TARGET).sqlite	\
		--out-dir output/$$base/$(TARGET)			\
		--forcefield $(forcefield)

output/%/$(TARGET)/out.png: $(addprefix output/%/$(TARGET)/,$(pngs))
	montage $^ -geometry 640x480\>+3+1 $@

# this is a phony recipe for testing ibstore code
.PHONY: temp
temp:
	python main.py --dataset datasets/small-opt.json \
		--sqlite-file $$(mktemp -d)/tmp.sqlite --out-dir /tmp

ARGS =
.PHONY: debug
debug:
	rm -r debug
	mkdir debug
	python debug.py $(ARGS)

datasets/cache/industry.json: datasets/industry.json
	python cache_dataset.py --dataset $< --output $@

plot.idivf:
	python plot.py \
idivf-sage-2.1.0 \
nc-tm-idivf-sage-2.1.0 \
r-nc-tm-idivf-sage-2.1.0 \
sage-2.1.0

# usage:
# $(call plot,FFS[,DIR][,FILTER][,NEGATE])
plot = python plot.py $1 $(if $2, -d $2) $(if $3, -f $3) $(if $4, -n)

# torsion multiplicity project with supplemental data set. now comparing both to
# sage 2.1 and 2.2
plot.tm:
	python plot.py sage-2.2.0 tm-2.2 ultra-tm-2.2
	sed -E -i 's/ -([0-9]+\.)/$$-$$\1/g' current/tabs/stats.tex
	cd current && pdflatex main.tex

plot.supp:
	python plot.py -d supp sage-2.2.0 tm-2.2 ultra-tm-2.2 -o current/figs/supp

# label ultra-tm-2.2 parameters with their associated record ids. it should be
# easiest to work backwards from the most specific parameters in ultra-tm to the
# parent parameters in tm-2.2 and sage-2.2
filters/ultra-tm.json:
	python label.py -c output/industry/ultra-tm-2.2 -f ultra-tm-2.2.offxml -o $@

plot.subsets:
	python plot.py sage-2.2.0 tm-2.2 ultra-tm-2.2 -r ultra-tm.dat -o current/figs/in_tm
	python plot.py sage-2.2.0 tm-2.2 ultra-tm-2.2 -r ultra-tm.dat -o current/figs/out_tm -n

plot.smee:
	python plot.py sage-2.1.0 smee-sage-2.1.0-opt -o /tmp
