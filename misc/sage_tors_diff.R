options(scipen = 999)

v1 <- read.csv("dump/sage-2.1.0.all.csv", header = FALSE)
v2 <- read.csv("dump/pavan-2.1.0.all.csv", header = FALSE)
v3 <- read.csv("dump/pavan-repeat.all.csv", header = FALSE)

colnames(v1) <- c("pid", "v1")
colnames(v2) <- c("pid", "v2")
colnames(v3) <- c("pid", "v3")

full <- merge(merge(v1, v2, sort = FALSE), v3, sort = FALSE)

# percent differences
full$p12 <- 100 * (full$v1 - full$v2) / full$v1
full$p13 <- 100 * (full$v1 - full$v3) / full$v1
full$p23 <- 100 * (full$v2 - full$v3) / full$v2

# regular differences
full$d12 <- full$v1 - full$v2
full$d13 <- full$v1 - full$v3
full$d23 <- full$v2 - full$v3

plot(full$p12, ylab = "%Diff")

full[which.max(full$p12), ]

full[order(abs(full$p12), decreasing = TRUE), ]

full[order(abs(full$p12), decreasing = TRUE), 1:7]

# [#1:1]-[*;r3:2]~;!@[*:3]

## variance in parameter value vs coverage
## - maybe find threshold for coverage

## keep an eye on t165-t167 too, should they be at the end? or always zero

full[order(abs(full$p12), decreasing = TRUE), ] |> head()
full[order(abs(full$p12), decreasing = TRUE), ] |> head()

full[order(abs(full$d13), decreasing = TRUE), ] |> head()
full[order(abs(full$d13), decreasing = TRUE), ] |> head()

bond_lengths <- full[grepl("-length", full$pid),]
bond_k <- full[grepl("^b.*-k", full$pid),]

angle_angle <- full[grepl("-angle", full$pid),]
angle_k <- full[grepl("^a.*-k", full$pid),]

torsions <- full[grepl("^t.*-k", full$pid),]
