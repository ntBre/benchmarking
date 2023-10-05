#!/bin/bash
#SBATCH -J espaloma-bench
#SBATCH -p standard
#SBATCH -t 144:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
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
       --forcefield espaloma-openff_unconstrained-2.1.0 \
       --dataset datasets/industry.json \
       --sqlite-file espaloma.sqlite \
       --out-dir output/industry/espaloma \
       --procs 16 \
       --invalidate-cache

date
