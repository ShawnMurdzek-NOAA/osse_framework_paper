#!/bin/sh

#SBATCH -A wrfruc
#SBATCH -t 01:00:00
#SBATCH --nodes=1
#SBATCH --mem=20GB
#SBATCH --partition=orion

. ~/.bashrc
my_py

date
python make_NR_MRMS_coverage_mask.py
date
