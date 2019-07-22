===================
in.cut_wire
===================

Purpose
=======
To cut a nanowire shape from a bulk sample and write the atom positions to a LAMMPS data file

Input
=======

LAMMPS restart file 

Output
=======

LAMMPS data file


Index Variables
================
	
	* ``WIRE_AXIS`` = 'x' or 'y' or 'z'
	* ``WIRE_RADIUS`` = *R* in Angstroms
	* ``WIRE_CENTER`` = *x* *y* in Angstroms
	* ``WIRE_LO`` = low bound of nanowire in Angstroms
	* ``WIRE_HI`` = upper bound of nanowire in Angstroms

	* ``DATA_TYPE`` = 'RESTART' only, for now, but can be easily changed, see in.deform for example.
	* ``DATA_FILE`` = *filenaùe*
	* ``DISTURB_ATOMS``  =  'no' (default) or 'yes' (not working properly)
	* ``REBOX_ATOMS`` = 'yes' (default, recommended)  

	* ``FOUT`` = filename for output LAMMPS data file (default *wire.dat*)

	* ``OUTDIR`` = output directory (default .)
	* ``SEED`` = a random positive integer for disturbing atoms (default 1225)

Example
========

.. code-block:: bash

	LAMMPS -in in.cut_wire \
	-var DATA_FILE 9000/bulk_120_120_300_min.dat/ff_yeon/restart_files/bulk.7815.restart \
	-var WIRE_AXIS z -var WIRE_RADIUS 30 -var WIRE_CENTER -20 13 -var WIRE_LO -100 -var WIRE_HI 0 \
	-var DISTURB_ATOMS no -var REBOX_ATOMS yes \
	-var FOUT wire_30_50_3.dat -log log.1

How it works
=============

TBC