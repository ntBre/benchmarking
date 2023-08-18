#!/bin/bash
#SBATCH -J tors-mul-bench
#SBATCH -p standard
#SBATCH -t 144:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o industry.out
#SBATCH -e industry.err

date
hostname

source ~/.bashrc
mamba activate ib-dev-new
module load imagemagick

make industry-output/out.png

date
