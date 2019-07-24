=================
Quickstart Guide
=================

A simple tutorial on how to cut out, prepare, and run a simulation deforming a silica nanowire.
	
Cutting out a wire from a bulk sample
======================================

More information on using this script can be found :doc:`here <../in-files/cut_wire>`

Required:
  * A LAMMPS executable. It can be the simple serial version.
  * *in.cut_wire* - the main script.
  * *in.cut_recenter* - a helper script.
  * A *DUMP* or *RESTART* file which has the atomic coordinates of the bulk sample 

.. note::

	Make sure the bulk sample is large enough; at least twice the radius of the nanowire.


:term:`CIV`
  * The cut axis
  * The wire radius
  * The wire length (top and lower boundaries)
  * Reboxing the cut wire 


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

More information on using this script can be found :doc:`here <../in-files/prepare_wire>`

With the cutting done we must now prepare the nanowire. This will ensure that the structure is relaxed i.e. the surface and core atoms are adjusted. We do this by a process of melting, quenching and relaxing under NPT and NVT conditions for several nanoseconds using bounding regions as appropriate.

We are giong to run this simulation on a GPU **without** minimizing the energy since ``minimize`` does not work with KOKKOS/CUDA 

Required:
  * *prepare.slurm*
  * in.prepare_slurm  
  * The LAMMPS *DATA* prepared earlier: **wire_30_100_1.dat**
  * LAMMPS executable (accelerated version)
  * The ReaxFF force-field file

First, edit *preapre.slurm* and change the following **KEY** variables necessary for the simulation:

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
	``MINIMIZE_CONFIG=0``                Do not minimize config before melting
	``RADIUS=30.6``                      Radius of nanowire in Angstroms
	``MACHINE=GPU``                      Run LAMMPS to run on GPU
	=================================   ===================================

Now launch the script on MATEIS303-r005 (or some standalone machine)
  
  .. code-block:: bash
		  
		  ./prepare.slurm > prep_$$.out &
		  disown

The first line launches the script and forwards output to a file while the second line makes sure the script keeps running even if the session is closed.
     
Once the job is done you should see a folder structure that looks something like:
::

   main
   ├── prepare.slurm
   ├── wire_30_100_1.dat
   ├── ffield_Yeon
   ├── prep_221.out
   └── 9000
       └── wire_30_100_1.dat         
           ├── log.in.prepare_wire.1
           ├── log.in.prepare_wire.2
   	   ├── atom_files
           │    ├── wire_prepare.7815.dump.1
           │    └── wire_prepare.7815.dump.2
           └── restart_files
               ├── pw.restart.210000
               ├── pw.restart.220000
	       ├── pw.restart.750000
	       ├── ...
	       ├── wire.1.7815.restart
	       └── wire.2.7815.restart

	       
.. warning::

   Some restart files will be overwritten when restarting from a previous timestep/run


.. note::

   During preparation of a nonowire you can pause/restart at any point by changing the variables listed above

   
Deforming a wire
====================

After finishing preparation you will now deform the nanowire.

Required:

  * deform.slurm
  * in.deform_slurm
  * *RESTART* file of prepared nanowire: wire.2.7815.restart
  * LAMMPS (accelerated)
  * ReaxFF force field parameters

As before you must edit *deform.slurm* and change some key variables which will control what the in.deform_wire will perform. *deform.slurm* is slightly different than *prepare.slurm*. Instead of a single simulation it is setup to carry out several simulations of the same type. 

.. list-table:: CIV for deform.slurm
	:widths: 50 25
	:header-rows: 1

	* - Variable
  	  - What does it do ?
	* - ``MACHINE=GPU`` 
	  - Run LAMMPS to run on GPU
	* - ``plist=(wire_30_100_1.dat)``
	  - Project name
	* - ``dlist=(9000/wire_30_100_1.dat/restart_files/wire.2.7815.restart)``
	  - The name of input-data file
	* - ``DATA_TYPE=RESTART``
	  - Type of input-data file to LAMMPS
	* - ``NATOM_TYPES=2``
	  - Only Si and O atoms are present
	* - ``SKIP=0``
	  - Suffix for output files
	* - ``MINIMIZE_CONFIG=0``
	  - Do not minimize config before melting
	* - ``TODO='EQUIL TENSION COMPRESSION DONE``
	  - Equilibrate, stretch, compress, exit
	* - ``DEF_MODE=LOAD``
	  - Deformation
	

You then run the script similarly to before on MATEIS303-r005 using a GPU

.. code-block:: bash
 
	./deform.slurm > deform_array_$$.out &
	disown

Once the job is done you should have a folder structure that looks similar to:

::

  8000/wire_30_100_1.dat/
  ├── log.in.deform_wire.0
  │ 
  ├── EQUIL
  │   ├── stress_strain_def.3121.LOAD.0.dat
  │   ├── atom_files
  │   │   └── wire_deform.3121.LOAD.0.dump.*
  │   └── restart_files
  │       ├── defw.eq.3121.restart
  │	  └── pw.restart.*
  │ 
  ├── TENSION
  │   ├── stress_strain_def.3121.LOAD.0.dat
  │   ├── atom_files
  │   │   └── wire_deform.3121.LOAD.0.dump.*
  │   └── restart_files
  │       ├── defw.load.3121.restart
  │	  └── pw.restart.*
  │ 
  ├── COMPRESSION
  │   ├── stress_strain_def.3121.LOAD.0.dat
  │   ├── atom_files
  │   │   └── wire_deform.3121.LOAD.0.dump.*
  │   └── restart_files
  │       ├── defw.load.3121.restart
  │	  └── pw.restart.*
  │ 
  └── DONE

  
Each subfolder contains one of the "TODO" elements, and each subfolder then contains *DUMP* and *RESTART* files along with the stress/strain measured along the z-direction. Any *DUMP* or *RESTART* file can be used to restart the simulation for that project, for example, for unloading or continuation of the loading.

.. attention::

   If you specify an ``EQUIL`` followed by ``TENSION`` and ``COMPRESSION``  in the ``TODO`` CIV then the tension and compression will use the *RESTART* file created at the end of the equilibration period. Otherwise the input-data file supplied will be used i.e. ``TODO`` list items should be considered as independent **AND NOT** sequential runs.
