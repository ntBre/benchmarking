ff=$1

echo generating input for force field $1

sbatch <<INP
#!/bin/bash
#SBATCH -J bench-$1
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
       --forcefield forcefields/$1.offxml \
       --dataset datasets/industry.json \
       --sqlite-file $1.sqlite \
       --out-dir output/industry/$1 \
       --procs 8 \
       --invalidate-cache

date
INP
