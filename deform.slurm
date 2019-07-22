#!/bin/bash
#SBATCH --job-name=wire20100
#SBATCH --output=run-%j.out
#SBATCH --error=run-%j.err
#SBATCH --partition=parallel2
#SBATCH --ntasks=56
#SBATCH --cpus-per-task=1
#SBATCH --time=48:00:00
hostname;pwd;date

plist=(wire_30_50_1_OH_10_rc_27.dump
       wire_30_50_1_OH_15_rc_27.dump
       wire_30_50_1_OH_5_rc_27.dump
       wire_30_50_2_OH_10_rc_27.dump
       wire_30_50_2_OH_15_rc_27.dump
       wire_30_50_2_OH_5_rc_27.dump
       wire_40_50_1_OH_10_rc_37.dump
       wire_40_50_1_OH_15_rc_37.dump
       wire_40_50_1_OH_5_rc_37.dump
       wire_40_50_2_OH_10_rc_37.dump
       wire_40_50_2_OH_15_rc_37.dump
       wire_40_50_2_OH_5_rc_37.dump)

dlist=(8000/wire_30_50_1_OH_10_rc_27.dump/EQUIL/restart_files/defw.min.19727.restart
       8000/wire_30_50_1_OH_15_rc_27.dump/EQUIL/restart_files/defw.min.2571.restart
       8000/wire_30_50_1_OH_5_rc_27.dump/EQUIL/restart_files/defw.min.7962.restart
       8000/wire_30_50_2_OH_10_rc_27.dump/EQUIL/restart_files/defw.min.26096.restart
       8000/wire_30_50_2_OH_15_rc_27.dump/EQUIL/restart_files/defw.min.2519.restart
       8000/wire_30_50_2_OH_5_rc_27.dump/EQUIL/restart_files/defw.min.7632.restart
       8000/wire_40_50_1_OH_10_rc_37.dump/EQUIL/restart_files/defw.min.28954.restart
       8000/wire_40_50_1_OH_15_rc_37.dump/EQUIL/restart_files/defw.min.30897.restart
       8000/wire_40_50_1_OH_5_rc_37.dump/EQUIL/restart_files/defw.min.7058.restart
       8000/wire_40_50_2_OH_10_rc_37.dump/EQUIL/restart_files/defw.min.17935.restart
       8000/wire_40_50_2_OH_15_rc_37.dump/EQUIL/restart_files/defw.min.6229.restart
       8000/wire_40_50_2_OH_5_rc_37.dump/EQUIL/restart_files/defw.min.11695.restart)

for ((i=0;i<${#plist[@]};++i)); do
    printf "%s --> %s\n" "${plist[i]}" "${dlist[i]}"

    INPUT=in.deform_wire
    PROJECT=${plist[i]}
    DATA_TYPE=RESTART
    DATA_FILE=${dlist[i]}
    SKIP=0

    TODO="EQUIL TENSION COMPRESSION DONE"
    DEF_MODE="LOAD"
    NATOM_TYPES=3

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
    -var MINIMIZE_CONFIG 0 \
    \
    -var DATA_FILE $DATA_FILE \
    -var DATA_TSTEP NAN \
    -var DATA_TYPE $DATA_TYPE \
    -var TODO $TODO \
    \
    -var DEF_MODE $DEF_MODE \
    -var FINAL_STRAIN 0.5 \
    -var INIT_STRAIN 0.0 \
    -var SRATE_SI 1e9 \
    \
    -log $OUTDIR/log.$INPUT.$SKIP.TC

    date
done
