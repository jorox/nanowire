#!/bin/bash
#SBATCH --job-name=wire20100
#SBATCH --output=run-%j.out
#SBATCH --error=run-%j.err
#SBATCH --partition=parallel2
#SBATCH --ntasks=56
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
hostname;pwd;date


MACHINE=GPU

plist=(wire_30_50_1.dat
       wire_30_50_2.dat)

dlist=(9000/wire_30_50_1.dat/restart_files/wire.2.19727.restart
       9000/wire_30_50_2.dat/restart_files/wire.2.2571.restart)


DATA_TYPE=RESTART
NATOM_TYPES=2
SKIP=0


MINIMIZE_CONFIG=0
TODO="EQUIL TENSION COMPRESSION DONE"
DEF_MODE="LOAD"
SRATE=1e9
INIT_STAIN=0
FINAL_STRAIN=0.5

############################################################################################
###################################### DO NOT EDIT THIS ####################################
############################################################################################
if [ $MACHINE = GPU ]
then 
    LMPMACHINE="mpirun -np 1 lmp_kokkos_cuda_mpi -k on g 1 -sf kk -pk kokkos neigh half neigh/qeq full newton on"
elif [ $MACHINE = CPU ]
then
    LMPMACHINE="mpirun -np $NTASKS lmp_kokkos_cuda_mpi"
fi

for ((i=0;i<${#plist[@]};++i)); do
    printf "%s --> %s\n" "${plist[i]}" "${dlist[i]}"

    INPUT=in.deform_wire
    PROJECT=${plist[i]}
    DATA_FILE=${dlist[i]}
    OUTDIR=$(pwd)/8000/${PROJECT}

    mkdir -p ${OUTDIR}

    echo ""
    echo ==================== JOB INFO ==================
    echo PROJECT = $PROJECT
    echo OUTDIR = $OUTDIR
    echo DATA FILE TYPE = $DATA_TYPE
    echo DATA FILE = $DATA_FILE
    echo RADIUS = $RADIUS
    echo TODO = $TODO
    echo DEF_MODE = $DEF_MODE
    echo SKIP = $SKIP
    echo ================================================
    echo ""

    #sed -i 's/Charge/q/g' $DATA_FILE
    
    mpirun -np 1 lmp_kokkos_cuda_mpi \
    -k on g 1 -sf kk -pk kokkos neigh half neigh/qeq full newton on \
    -in $INPUT \
    -var OUTDIR $OUTDIR \
    -var SEED $RANDOM \
    -var NATOM_TYPES $NATOM_TYPES \
    -var RADIUS_NW nan \
    -var SKIP $SKIP \
    -var MINIMIZE_CONFIG $MINIMIZE_CONFIG \
    \
    -var DATA_FILE $DATA_FILE \
    -var DATA_TSTEP NAN \
    -var DATA_TYPE $DATA_TYPE \
    -var TODO $TODO \
    \
    -var DEF_MODE $DEF_MODE \
    -var FINAL_STRAIN $FINAL_STRAIN \
    -var INIT_STRAIN $INIT_STRAIN \
    -var SRATE_SI $SRATE \
    \
    -log $OUTDIR/log.$INPUT.$SKIP.TC

    date
done
