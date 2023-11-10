# comparing new and old forcebalance versions

old <- read.csv("output/industry/sage-2.1.0/dde.csv")

new <- read.csv("output/industry/my-sage-2.1.0/dde.csv")

d <- merge(new, old, by='X')
colnames(d) = c("id", "new", "old")
d$diff <- abs(d$new - d$old)
d$signed <- d$new - d$old
head(d)

png(file="/tmp/out.png")
hist(d$diff[d$diff > 8], xlab="Abs. Diff.", main="DDE differences > 8 kcal/mol")
dev.off()

png(file="/tmp/out.png")
hist(d$signed[abs(d$signed) > 5], xlab="Diff.", main="DDE differences > 5 kcal/mol", breaks=50)
dev.off()

old.better <- d[abs(d$old) < abs(d$new),]

png(file="/tmp/out.png")
hist(old.better$diff[old.better$diff > 8], xlab="Abs. Diff.", main="DDE differences > 8 kcal/mol")
dev.off()
