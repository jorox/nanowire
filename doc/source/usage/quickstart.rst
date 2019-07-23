=================
Quickstart Guide
=================

A simple tutorial on how to cut out, prepare, and run a simulation deforming a silica nanowire.
	
Cutting out a wire from a bulk sample
======================================

Required:
  * A LAMMPS executable. It can be the simple serial version.
  * *in.cut_wire* - the main script.
  * *in.cut_recenter* - a helper script.
  * A *DUMP* or *RESTART* [#f1]_ file which has the atomic coordinates of the bulk sample 

.. note::

	Make sure the bulk sample is large enough; at least twice the radius of the nanowire.


:term:`CIV`
  * The cut axis
  * The wire radius
  * The wire length (top and lower boundaries)
  * Reboxing the cut wire 

More information can be found :doc:`here <cut_wire>`


To cut out a **R=30A**, **L=100A** wire from a 120A x 120A x 300A relaxed bulk sample along the **x-axis** and **rebox it** we issue

Example,
  .. code-block:: bash

	LAMMPS -in in.cut_wire \
	-var DATA_FILE 9000/bulk_120_120_300_min.dat/ff_yeon/restart_files/bulk.7815.restart \
	-var WIRE_AXIS x -var WIRE_RADIUS 30 -var WIRE_CENTER -20 13 -var WIRE_LO -100 -var WIRE_HI 0 \
	-var DISTURB_ATOMS no -var REBOX_ATOMS yes \
	-var FOUT wire_30_100_1.dat -log log.1

This will produce a LAMMPS *DATA* file **wire_R_L_AXIS.dat** which contains atom coordinates of a nanowire with its axis along the z-axis.

Preparing a wire
====================

After cutting out a nanowire we must prepare it. Relax the surface and core atoms. We do this by melting at 4000K, and then cooling "slowly" to 300K, and we relax the structure under NPT and NVT conditions for several nanoseconds.

Required:
  * *prepare.slurm*
  * LAMMPS *DATA* file created containing the nanowire
  * LAMMPS
  * Force-field file

Edit *preapre.slurm* and change the following **KEY** variables:

.. table :: 
	:widths: auto

	=================================   ===================================
	Variable   			    What does it do ?
	=================================   ===================================
	``PROJECT=wire_30_100_1.dat``        Project name
	``DATA_TYPE=DATA``                   Type of input-data file to LAMMPS
	``DATA_FILE=wire_30_100_1.dat``      The name of input-data file
	``SKIP=0``                           Suffix for output files
	``JUMP=MELT``                        Start with melting
	``RADIUS=30.6``                      Radius of nanowire in Angstroms
	``MACHINE=CPU``                      Changes LAMMPS to run on CPU/GPU
	``NTASKS=1``                         Number of MPI tasks to launch
	=================================   ===================================


Then launch the script,

* MATEIS303-R005 or some standalone machine
  
  .. code-block:: bash
		  
		  ./prepare.slurm

* P2CHPD (Dont forget to set the SLURM paramaters)
  
  .. code-block:: bash

		  sbatch prepare.slurm
	
This will create a folder structure in the same location as *prepare.slurm*:

.. code-block:: bash

  $ ls
  9000/wire_30_100_1.dat/atom_files
  9000/wire_30_100_1.dat/restart_files

.. warning::

   Some restart files will be overwritten when restarting from a previous timestep/run


.. note::

   During preparation of a nonowire you can pause/restart at any point by changing the variables listed above

   
Deforming a wire
====================

Once the NW is ready for deformation we use deform.slurm to perform the actual deformation

Example

.. code-block:: bash
 
	./deform.slurm


.. rubric:: Footnotes

.. [#f1] To read *RESTART* files you must use the same executable they were created with. Otherwise you must convert 
