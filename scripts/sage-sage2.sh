#!/bin/bash
#SBATCH -J bench-2.1.0
#SBATCH -p standard
#SBATCH -t 84:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch

date
hostname

source ~/.bashrc
mamba activate ib-dev-esp

python main.py \
       --forcefield forcefields/sage-sage-new-filter.offxml \
       --dataset datasets/industry.json \
       --sqlite-file sage-sage.sqlite \
       --out-dir output/industry/sage-sage-new \
       --procs 8 \
       --invalidate-cache

date
