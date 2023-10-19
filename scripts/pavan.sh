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
       --forcefield forcefields/pavan-2.1.0.offxml \
       --dataset datasets/industry.json \
       --sqlite-file pavan.sqlite \
       --out-dir output/industry/pavan-2.1.0-repeat \
       --procs 8 \
       --invalidate-cache

date
