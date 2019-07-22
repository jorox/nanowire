=================
Quickstart Guide
=================

This will help you prepare and run a simulation deforming a silica nanowire


File types
==============

\*.in files 
	Are LAMMPS script files.
	
\*.slurm files 
	Are BASH files for job(s) to run on P2CHPD or MATEIS303-r05
	
Cutting out a wire
===================

Silica NW are cut out of a bulk sample. 
The sample must be large enough. A 120A x 120A x 300A relaxed bulk sample is provided here.

Example,

.. code-block:: bash

	LAMMPS -in in.cut_wire \
	-var DATA_FILE 9000/bulk_120_120_300_min.dat/ff_yeon/restart_files/bulk.7815.restart \
	-var WIRE_AXIS z -var WIRE_RADIUS 30 -var WIRE_CENTER -20 13 -var WIRE_LO -100 -var WIRE_HI 0 \
	-var DISTURB_ATOMS no -var REBOX_ATOMS yes \
	-var FOUT wire_30_50_3.dat -log log.1


Preparing a wire
====================

After cutting out a NW we prepare using prepare.slurm:

1. Melting at 4000K then quenching "slowly" to 300K
2. Relaxation using NVT with wall
3. Relaxation using NPH with wall
4. Relaxation using NPH without a wall

Example

.. code-block:: bash

	./prepare.slurm wire_30_50_3.data DATA wire_30_50_3.data 0 MELT 30
	

Deforming a wire
====================

Once the NW is ready for deformation we use deform.slurm to perform the actual deformation

Example

.. code-block:: bash
	
	./deform.slurm