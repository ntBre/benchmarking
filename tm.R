## load the triage data files and limit the results to the torsions

sage_full <- read.table("sage-2.1.0.triage.dat", header = TRUE)
sage_torsions <- sage_full[grepl("t", sage_full$param),]

tm_full <- read.table("tm.triage.dat", header = TRUE)
tm_torsions <- tm_full[grepl("t", tm_full$param),]

sage_tm_full <- read.table("sage-tm.triage.dat", header = TRUE)
sage_tm_torsions <- sage_tm_full[grepl("t", sage_tm_full$param),]

## load the list of new parameters
new_params <- read.table("../valence-fitting/new_params.dat")

sage <- sage_torsions[sage_torsions$param %in% new_params$V1,]

tm <- tm_torsions[tm_torsions$param %in% new_params$V1,]
