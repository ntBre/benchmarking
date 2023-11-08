# checking the differences between benchmark runs

p1 <- read.csv("pavan-2.1.0/dde.csv")
p2 <- read.csv("pavan-2.1.0-repeat/dde.csv")
ddes <- merge(p1, p2, by="X")
colnames(ddes) = c("id", "p1", "p2")

big.ddes <- ddes[abs(ddes$p1 - ddes$p2) > 1,]
big.ddes$diff <- abs(big.ddes$p1 - big.ddes$p2)

png(file="/tmp/ddes.png", width=960, height=960, res=200)
hist(big.ddes$diff, xlab="Abs. Diff.", main="DDEs")
dev.off()

# RMSDs
p1 <- read.csv("pavan-2.1.0/rmsd.csv")
p2 <- read.csv("pavan-2.1.0-repeat/rmsd.csv")
rmsd <- merge(p1, p2, by="X")
colnames(rmsd) = c("id", "p1", "p2")

big.rmsd <- rmsd[abs(rmsd$p1 - rmsd$p2) > 1e-2,]
big.rmsd$diff <- abs(big.rmsd$p1 - big.rmsd$p2)

png(file="/tmp/rmsd.png", width=960, height=960, res=200)
hist(big.rmsd$diff, xlab="Abs. Diff.", main="RMSD")
dev.off()

# TFDs
p1 <- read.csv("pavan-2.1.0/tfd.csv")
p2 <- read.csv("pavan-2.1.0-repeat/tfd.csv")
tfd <- merge(p1, p2, by="X")
colnames(tfd) = c("id", "p1", "p2")

big.tfd <- tfd[abs(tfd$p1 - tfd$p2) > 1e-2,]
big.tfd$diff <- abs(big.tfd$p1 - big.tfd$p2)
png(file="/tmp/tfd.png", width=960, height=960, res=200)
hist(big.tfd$diff, xlab="Abs. Diff.", main="TFD")
dev.off()
