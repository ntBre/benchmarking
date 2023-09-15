#!/bin/bash
#SBATCH -J tm
#SBATCH -p standard
#SBATCH -t 72:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o tm.out
#SBATCH -e tm.err

date
hostname

source ~/.bashrc
mamba activate ib-dev-new
module load imagemagick

target=tm
make output/industry/$target/out.png TARGET=$target

date
