#!/bin/bash
#SBATCH -J sage-tm
#SBATCH -p standard
#SBATCH -t 24:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o sage-tm.out
#SBATCH -e sage-tm.err

date
hostname

source ~/.bashrc
mamba activate ib-dev-new
module load imagemagick

target=sage-tm
make output/industry/$target/out.png TARGET=$target

date
