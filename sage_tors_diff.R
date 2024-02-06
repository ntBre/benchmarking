v1 <- read.csv("dump/sage-2.1.0.csv", header = FALSE)
v2 <- read.csv("dump/pavan-2.1.0.csv", header = FALSE)
v3 <- read.csv("dump/pavan-repeat.csv", header = FALSE)

colnames(v1) <- c("pid", "v1")
colnames(v2) <- c("pid", "v2")
colnames(v3) <- c("pid", "v3")

full <- merge(merge(v1, v2, sort = FALSE), v3, sort = FALSE)

# percent differences
full$p12 <- 100 * (full$v1 - full$v2) / full$v1
full$p13 <- 100 * (full$v1 - full$v3) / full$v1
full$p23 <- 200 * (full$v2 - full$v3) / full$v2

plot(full$p12, ylab = "%Diff")

full[which.max(full$p12), ]

full[order(abs(full$p12), decreasing = TRUE), ] |> head()
full[order(abs(full$p13), decreasing = TRUE), ] |> head()
