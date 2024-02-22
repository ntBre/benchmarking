#!/usr/bin/Rscript

debug <- Sys.getenv("RDEBUG")

args <- commandArgs(trailingOnly = TRUE)
csv1 <- read.csv(args[1], header = TRUE)
csv2 <- read.csv(args[2], header = TRUE)

stopifnot(length(csv1$X) == length(csv2$X))

both <- merge(csv1, csv2, by = "X")
colnames(both) <- c("id", "v1", "v2")

diff <- both$v1 - both$v2
print(sprintf("maximum difference: %f, mean: %f", max(diff), mean(diff)))

if (debug == 1) {
    both[which.max(diff), ]
} else if (debug > 1) {
    both$diff <- diff
    head(both[order(abs(diff), decreasing = TRUE), ], n = as.integer(debug))
}
