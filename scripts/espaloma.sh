#!/bin/bash
#SBATCH -J espaloma-bench
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
mamba activate ib-dev-esp

python main.py \
       --forcefield espaloma-openff_unconstrained-2.1.0 \
       --dataset datasets/industry.json \
       --sqlite-file espaloma.sqlite \
       --out-dir output/industry/espaloma \
       --procs 8 \
       --invalidate-cache

date
