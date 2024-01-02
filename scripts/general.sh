ff=$1
shift
ncpus=8
hours=84
mem=32

while getopts "c:t:m:h" arg; do
	case $arg in
		h) echo 'usage: [-c CPUS] [-t CPU_HOURS] [-m GB_MEMORY] [-h]' ;;
		c) ncpus=$OPTARG ;;
		t) hours=$OPTARG ;;
		m) mem=$OPTARG ;;
	esac
done

echo generating input for force field $ff, with $ncpus cpus, $mem gb, and $hours hours

sbatch <<INP
#!/bin/bash
#SBATCH -J ib-$ff
#SBATCH -p standard
#SBATCH -t $hours:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=$ncpus
#SBATCH --mem=${mem}gb
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mail-user=bwestbr1@uci.edu
#SBATCH --constraint=fastscratch

date
hostname

source ~/.bashrc
mamba activate ib-dev-esp

python main.py \
       --forcefield forcefields/$ff.offxml \
       --dataset datasets/industry.json \
       --sqlite-file $ff.sqlite \
       --out-dir output/industry/$ff \
       --procs $ncpus \
       --invalidate-cache

date
INP
