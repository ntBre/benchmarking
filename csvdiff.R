args <- commandArgs(trailingOnly = TRUE)
csv1 <- read.csv(args[1], header = TRUE)
csv2 <- read.csv(args[2], header = TRUE)

both <- merge(csv1, csv2, by = "X")
colnames(both) <- c("id", "v1", "v2")

print("maximum difference:")
max(both$v1 - both$v2)
both[which.max(both$v1 - both$v2), ]
