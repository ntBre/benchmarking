#!/bin/bash
#SBATCH -J besmarts-ba-bench
#SBATCH -p standard
#SBATCH -t 84:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch

date
hostname

source ~/.bashrc
mamba activate ib-dev-new

python main.py \
       --forcefield forcefields/besmarts-ba.offxml \
       --dataset datasets/industry.json \
       --sqlite-file besmarts-ba.sqlite \
       --out-dir output/industry/besmarts-ba \
       --procs 8
       --invalidate-cache

date
