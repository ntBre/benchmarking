#!/bin/bash
#SBATCH -J my-sage-bench
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
mamba activate ib-dev-new

python main.py \
       --forcefield forcefields/my-sage-2.1.0.offxml \
       --dataset datasets/industry.json \
       --sqlite-file my-sage.sqlite \
       --out-dir output/industry/my-sage-2.1.0 \
       --procs 8 \
       --invalidate-cache

date
