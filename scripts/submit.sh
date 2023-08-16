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
#SBATCH -o slurm.out
#SBATCH -e slurm.err

date
hostname

source ~/.bashrc
mamba activate bench-dev
module load imagemagick

make output/out.png

date
