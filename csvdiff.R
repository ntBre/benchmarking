#!/usr/bin/Rscript

debug <- Sys.getenv("RDEBUG") == 1

args <- commandArgs(trailingOnly = TRUE)
csv1 <- read.csv(args[1], header = TRUE)
csv2 <- read.csv(args[2], header = TRUE)

stopifnot(length(csv1$X) == length(csv2$X))

both <- merge(csv1, csv2, by = "X")
colnames(both) <- c("id", "v1", "v2")

print(sprintf("maximum difference: %f", max(both$v1 - both$v2)))

if (debug) {
    both[which.max(both$v1 - both$v2), ]
}
