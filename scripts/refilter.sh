#!/bin/bash
#SBATCH -J refilter-industry
#SBATCH -p standard
#SBATCH -t 144:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=64gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o refilter.out
#SBATCH -e refilter.err

date
hostname

source ~/.bashrc
mamba activate ib-dev-new

python refilter.py --nprocs=32

date
