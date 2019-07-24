#!/bin/bash
#SBATCH --job-name=runSp4300
#SBATCH --output=run-%j.out
#SBATCH --error=run-%j.err
#SBATCH --partition=parallel2
#SBATCH --ntasks=40
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
hostname;pwd;date

#################### Edit this to change job ##################
PROJECT=
DATA_TYPE=
DATA_FILE=
SKIP=
JUMP=
RADIUS=

NATOM_TYPES=2 #assuming only Si and O atom types
MINIMIZE_CONFIG=1

OUTDIR=$(pwd)/9000/${PROJECT}
MACHINE=CPU #CPU
NTASKS=1 # num of cpu tasks, set to $SLURM_NTASKS
###############################################################



################### Dont need to touch this ###########################

# Some stuff
INPUT=in.prepare_wire #LAMMPS script
mkdir -p $OUTDIR/restart_files #create needed folders
mkdir -p $OUTDIR/atom_files

# Run on GPU/CPU
if [ $MACHINE = GPU ]
then 
    LMPMACHINE="mpirun -np 1 lmp_kokkos_cuda_mpi -k on g 1 -sf kk -pk kokkos neigh half neigh/qeq full newton on"
elif [ $MACHINE = CPU ]
then
    LMPMACHINE="mpirun -np $NTASKS lmp_kokkos_cuda_mpi"
fi

# Print job info to log file (screen)
echo ""
echo ==================== JOB INFO ==================
echo PROJECT = $PROJECT
echo OUTDIR = $OUTDIR
echo DATA FILE TYPE = $DATA_TYPE
echo DATA FILE = $DATA_FILE
echo RADIUS = $RADIUS
echo ================================================
echo ""


$LMPMACHINE \
-in $INPUT \
\
-var RADIUS_NW $RADIUS \
-var NATOM_TYPES $NATOM_TYPES \
\
-var JUMP_SECTION $JUMP \
-var MINIMIZE_CONFIG $MINIMIZE_CONFIG \
-var OUTDIR $OUTDIR \
-var SEED $RANDOM \
\
-var DATA_FILE $DATA_FILE \
-var DATA_TYPE $DATA_TYPE \
-var SKIP $SKIP \
-var SEED $RANDOM \
\
-log $OUTDIR/log.$INPUT.$SKIP


date
