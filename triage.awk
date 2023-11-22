#!/usr/bin/awk -f

NR == 1 {
    print
}

NR > 1 && $2 > 10000 && $1 !~ /t/ {
    print | "sort -nrk3"
}
