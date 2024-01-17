#!/bin/sh

# usage:
# compare.sh <parameter> filename.offxml...

pat=$1
shift

awk -v pat=$pat '
last != FILENAME {
	print ""
	print FILENAME
	last = FILENAME
}
$0 ~ pat {
	gsub(/^ +<Proper /, "")
	gsub(/periodicity.="."/, "")
	gsub(/phase.="[^"]+"/, "")
	gsub(/ k.="[^"]+"/, "")
	gsub(/ idivf.="[^"]+"/, "")
	gsub(/ parameterize="[^"]+"/, "")
	gsub(/ +/, " ")
	print
}' $@
