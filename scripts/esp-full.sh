#!/bin/bash
#SBATCH -J esp-full
#SBATCH -p standard
#SBATCH -t 144:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch
#SBATCH -o esp-full.out
#SBATCH -e esp-full.err

date
hostname

source ~/.bashrc
mamba activate ib-dev-new
module load imagemagick

target=esp-full
make output/industry/$target/out.png TARGET=$target

date
