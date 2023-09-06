# datasets/full-opt.json

csvs := dde.csv rmsd.csv tfd.csv
pngs := $(subst .csv,.png,$(csvs))

# for specifying a subdirectory of output
TARGET =

forcefield = force-field.offxml
ifdef TARGET
    forcefield = $(TARGET).offxml
endif

$(addprefix output/%/$(TARGET)/,$(csvs) $(pngs)) %.sqlite: datasets/%.json main.py
# DO NOT run M-x align here, it adds spaces around the bash =
	base=$(basename $(notdir $<));					\
	mkdir -p output/$$base/$(TARGET);				\
	python main.py --dataset $< --db-file $$base.$(TARGET).sqlite	\
		--out-dir output/$$base/$(TARGET)			\
		--forcefield $(forcefield)

output/%/$(TARGET)/out.png: $(addprefix output/%/$(TARGET)/,$(pngs))
	montage $^ -geometry 640x480\>+3+1 $@

# this is a phony recipe for testing ibstore code
.PHONY: temp
temp:
	python main.py --dataset datasets/small-opt.json \
		--db-file $$(mktemp -d)/tmp.sqlite --out-dir /tmp

ARGS =
.PHONY: debug
debug:
	rm -r debug
	mkdir debug
	python debug.py $(ARGS)
