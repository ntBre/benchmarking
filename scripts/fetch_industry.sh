#!/bin/bash
#SBATCH -J fetch-industry
#SBATCH -p standard
#SBATCH -t 144:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10000mb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o fetch.out
#SBATCH -e fetch.err

date
hostname

source ~/.bashrc
mamba activate bench-dev

make datasets/industry.json

date
