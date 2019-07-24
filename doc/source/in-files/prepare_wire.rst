================
in.prepare_wire
================

Purpose
========

To prepare nanowires for deformation after they have been cut out of a bulk sample.
This script will make sure that the nanowire has "forgotten" its old bulk state.
This means that the core and surface atoms have reorganized into their new positions.

Index variables
================

	* ``SKIP`` = differentiate between DUMP files
	* ``JUMP_SECTION`` = *MELT* or *COOL* or *RELAX* or *EQUIL* or *TEST* or *DONE*
	* ``DATA_TYPE`` = *RESTART* or *DATA*
	* ``DATA_FILE`` = File-name for input data
	* ``RADIUS_NW`` = Radius of nanowire for ``fix wall/region``
	* ``SEED`` = positive integer (default: 23154)
	* ``TEMP_RELAX`` = relaxation temperature in Kelvins (default: 300)
	* ``TEMP_HEAT``  = melting temperature in Kelvins (default: 4000)
	* ``MINIMIZE_CONFIG`` = minimize configuration

Example
=========

Minimize a nanowire on MATEIS303-r005 using 6 processors:

.. code-block:: bash

	PROJECT=wire_40_50_3.dat
	INPUT=in.prepare_wire
	OUTDIR=$(pwd)/9000/${PROJECT}

	mpirun -np 6 lmp_kokkos_cuda_mpi \
	-in $INPUT \
	\
	-var RADIUS_NW $RADIUS \
	-var NATOM_TYPES 2 \
	\
	-var JUMP_SECTION MELT \
	-var MINIMIZE_CONFIG 1 \
	-var OUTDIR $OUTDIR \
	-var SEED $RANDOM \
	\
	-var DATA_FILE wire_40_50_3.dat \
	-var DATA_TYPE DATA \
	-var SKIP 0 \
	\
	-log $OUTDIR/log.$INPUT.0

You can find the name of the last restart file created by issuing

.. code-block:: bash

	ls -ltr 9000/wire_40_50_3.dat/restart_files/pw.restart.*

This will list the files in order of creation. The last one will be the most recent.
Use the last restart file to continue preparation using the GPU since it is faster

.. code-block:: bash 

	PROJECT=wire_40_50_3.dat
	INPUT=in.prepare_wire
	OUTDIR=$(pwd)/9000/${PROJECT}

	mpirun -np 1 lmp_kokkos_cuda_mpi \
	-k on g 1 -sf kk -pk kokkos neigh half neigh/qeq full newton on \
	-in $INPUT \
	\
	-var RADIUS_NW 40.8 \
	-var NATOM_TYPES 2 \
	\
	-var JUMP_SECTION MELT \
	-var MINIMIZE_CONFIG 0 \
	-var OUTDIR $OUTDIR \
	-var SEED $RANDOM \
	\
	-var DATA_FILE 9000/wire_40_50_3.dat/restart_files/pw.restart.40000 \
	-var DATA_TYPE RESTART \
	-var SKIP 1 \
	\
	-log $OUTDIR/log.$INPUT.1


Input
=======

* *RESTART*
* *DATA*
* 2 to 4 atom types

Output
========

* Restart files

	* ``${OUTDIR}/restart_files/pw.restart`` = general restart files, frequency 10000 steps
	* ``${OUTDIR}/restart_files/wire.m2.${SEED}.restart`` = melting section restart files, frequency 1
	* ``${OUTDIR}/restart_files/wire.m1.${SEED}.restart`` = cooling section restart files, frequency 1
	* ``${OUTDIR}/restart_files/wire.0.${SEED}.restart`` = relaxation section restart files, frequency 1
	* ``${OUTDIR}/restart_files/wire.1.${SEED}.restart`` = equilibration section restart files, frequency 1
	* ``${OUTDIR}/restart_files/wire.2.${SEED}.restart`` = testing section restart files, frequency 1
 
* Dump files
	
	* wire_prepare.${SEED}.dump.${SKIP}

Sections
==========

0. Minimize energy
1. Melt = 250ps / NVE + Langevin + wall/region / ``${TEMP_HEAT}``
2. Cool = 5K/ps / NVE + Langevin + wall/region / ``${TEMP_HEAT}`` --> ``${TEMP_RELAX}`` 5K/ps
3. Relax = 500ps / NVE + Langevin + wall/reflect / ``${TEMP_RELAX}``
4. Equil = 500ps / NPH + Langevin + wall/reflect / 300K, z = 0bar
5. Test = 50ps / NPH +  Langevin / 300K, z=0bar