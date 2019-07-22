===================
Deforming a wire
===================

in.deform_wire

Purpose
========

To deform a prepared nanowire in tension and compression under loading or unloading

.. attention::

	This is a very versatile script, and contains a lot of different control variables 

.. warning::

	Always include a "DONE" at the end of the ``TODO`` variable

.. attention::
	
	Although this code is used for deformation, it does include an initial 500 ps equilibration section

.. warning::

	When using ``DEF_MODE UNLOAD`` make sure you set the correct ``INIT_STRAIN``
	``DEF_MODE UNLOAD`` has not yet been tested

Index variables
================
	* Input-related variables
		
		* ``DATA_TYPE`` = *RESTART* or *DATA* or *DUMP*
		* ``DATA_FILE`` = File-name
		* ``DUMP_READ_STEP`` = *integer* timestep in *DUMP* file
		* ``RADIUS_NW`` = radius of nanowire in Angstroms

	* Control variables
		
		* ``TODO`` = list one or more of "EQUIL" "TENSION" "COMPRESSION" and "DONE" as final entry
		* ``MINIMIZE_CONFIG`` = *False* or *True* (default:False, case-sensitive)
	
	* Output-related variables

		* ``SEED`` = random positive integer (default: 23154)
		* ``SKIP`` = suffix for output files
		* ``T_DUMP`` = in femtoseconds output stress/strain and atom-config (default=200)
	
	* Other option variables
	
		* ``TEMP_RELAX`` = temperature during deformation (default=300)
		*	``TEMP_EQ``  = temperature fpr *EQUIL* section (default=300)

	* Deformation-related variables

		* ``DEF_MODE`` = "LOAD" or "UNLOAD"
		* ``DEF_STAGGER`` = staggerd or continuous deformation "yes" (default) or "no"
		* ``SRATE_SI`` = deformation speed in s^-1 (default=1e9) #
		* ``INIT_STRAIN`` = initial strain if restating from deformation (default=0)
		* ``FINAL_STRAIN`` = final target strain (default=0.5)

	
Examples
=========

Minimize a hydroxylated prepared nanowire on MATEIS303-r005

.. code-block:: bash

    INPUT=in.deform_wire
    PROJECT=wire_30_50_1_OH_10_rc_27.dump
    DATA_FILE=wire_30_50_1_OH_10_rc_27.dump
    DATA_TYPE=DUMP
    SKIP=MIN

    TODO="EQUIL DONE"
    DEF_MODE="LOAD"
    NATOM_TYPES=3

    OUTDIR=$(pwd)/8000/${PROJECT}

    mpirun -np 6 lmp_kokkos_cuda_mpi \
    -in $INPUT \
    -var OUTDIR $OUTDIR \
    -var SEED $RANDOM \
    -var NATOM_TYPES $NATOM_TYPES \
    -var RADIUS_NW nan \
    -var SKIP $SKIP \
    -var MINIMIZE_CONFIG 1 \
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
    -log $OUTDIR/log.$INPUT.$SKIP

Equilibrate and then deform a minimized R=30 L=100 OH=10/nm^2 nanowire in loading (tension and compression)

.. code-block:: bash

    INPUT=in.deform_wire
    PROJECT=wire_30_50_1_OH_10_rc_27.dump
    DATA_FILE=8000/wire_30_50_1_OH_10_rc_27.dump/EQUIL/restart_files/defw.min.19727.restart
    DATA_TYPE=RESTART
    SKIP=0

    TODO="EQUIL TENSION COMPRESSION DONE"
    DEF_MODE="LOAD"
    NATOM_TYPES=3

    OUTDIR=$(pwd)/8000/${PROJECT}

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

