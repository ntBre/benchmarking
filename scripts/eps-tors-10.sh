#!/bin/bash
#SBATCH -J eps-tors-10
#SBATCH -p standard
#SBATCH -t 144:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o sage.out
#SBATCH -e sage.err

date
hostname

source ~/.bashrc
mamba activate ib-dev-new
module load imagemagick

target=eps-tors-10
make output/industry/$target/out.png TARGET=$target

date
