#!/bin/bash
#SBATCH --job-name=runSp4300
#SBATCH --output=run-%j.out
#SBATCH --error=run-%j.err
#SBATCH --partition=parallel2
#SBATCH --ntasks=40
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
hostname;pwd;date

PROJECT=$1
DATA_TYPE=$2
DATA_FILE=$3
SKIP=$4
JUMP=$5
RADIUS=$6

INPUT=in.prepare_wire
OUTDIR=$(pwd)/9000/${PROJECT}

mkdir -p $OUTDIR/restart_files
mkdir -p $OUTDIR/atom_files

echo ""
echo ==================== JOB INFO ==================
echo PROJECT = $PROJECT
echo OUTDIR = $OUTDIR
echo DATA FILE TYPE = $DATA_TYPE
echo DATA FILE = $DATA_FILE
echo RADIUS = $RADIUS
echo ================================================
echo ""


#To run on CPU:  DELETE first two lines and replace by
#mpirun -np 6 lmp_kokkos_cuda_mpi \

# Run on GPU
mpirun -np 1 lmp_kokkos_cuda_mpi \
-k on g 1 -sf kk -pk kokkos neigh half neigh/qeq full newton on \
-in $INPUT \
\
-var RADIUS_NW $RADIUS \
-var NATOM_TYPES 2 \
\
-var JUMP_SECTION $JUMP \
-var MINIMIZE_CONFIG 0 \
-var OUTDIR $OUTDIR \
-var SEED $RANDOM \
\
-var DATA_FILE $DATA_FILE \
-var DATA_TYPE $DATA_TYPE \
-var SKIP $SKIP \
\
-log $OUTDIR/log.$INPUT.$SKIP


date
