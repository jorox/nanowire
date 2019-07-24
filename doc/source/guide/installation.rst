=====================
Required software
=====================

LAMMPS
=======

Required Libraries:
	* MPI (openMPI works best)
	* CUDA

Supported compilers
	* Intel
	* GCC (<=8.2) [#f2]_

This will help you compile LAMMPS with ReaxFF and KOKKOS/CUDA.
Make sure you have the required library files and headers. This guide does not cover how to do that.

#. Clone the LAMMPS directory to your home folder:

   .. code-block:: bash

      cd $HOME
      git clone -b stable https://github.com/lammps/lammps.git lammps-stable
      cd lammps-stable/src

   .. note::

      If you dont have git you can download a tarball (140 MB) from https://lammps.sandia.gov/download.html

#. Install User-Reax/C, MISC, and MANYBODY packages

   .. code-block:: bash

      make yes-user-reaxc
      make yes-misc
      make yes-manybody

#. Create a KOKKOS/CUDA Makefile

   .. code-block:: bash

      mkdir -p MAKE/MINE
      cp MAKE/OPTIONS/Makefile.kokkos_cuda_mpi MAKE/MINE/

#. Find out the name of your NVIDIA card

   .. code-block:: bash

      nvidia-smi

#. Find the CUDA-CC (compute capability) of your card at https://developer.nvidia.com/cuda-gpus.  For instance, Titan V has CC = 7.0

#. Edit the Makefile; change ``KOKKOS_ARCH = Kepler35`` to ``KOKKOS_ARCH = Volta70`` or to the CUDA-CC you have
	
   .. code-block:: bash

      vim MAKE/MINE/Makefile.kokkos_cuda_mpi

   .. note::

      For other CUDA CC designations in the MAKEFILE check https://lammps.sandia.gov/doc/Build_extras.html#kokkos or lammps-stable/lib/kokkos/README
	
#. Link nvcc-wrapper to $HOME/bin [#f1]_

   .. code-block:: bash
	
      mkdir $HOME/bin
      ln -s $HOME/lammps-stable/lib/kokkos/bin/nvcc_wrapper $HOME/bin

#. Parallel compile LAMMPS. Change ``-j4`` to the number of processors you want to use

   .. code-block:: bash

      make -j4 kokkos_cuda_mpi

#. You should now have an executable **lmp_kokkos_cuda_mpi** in your LAMMPS src folder. Add this file to your $PATH

   #. create a .local/bin directory

      .. code-block:: bash
	
         mkdir -p $HOME/.local/bin
         ln -s $HOME/lammps-stable/src/lmp_kokkos_cuda_mpi $HOME/.local/bin/

   #. edit your enviroment file ``vim $HOME/.bashrc``, and add the following line to the end of the file

      .. code-block:: bash
	
         PATH="$HOME/.local/bin:$PATH"
         export PATH

   #. restart your session or use ``source $HOME/.bashrc`` for the change to take effect


OVITO
======

Download and install OVITO from here <https://ovito.org/index.php/download>
It is needed to hydroxylate and methylate silica nanowires

.. rubric:: Footnotes
		
.. [#f1] KOKKOS uses a wrapper to compile LAMMPS files. For some reason it aways looks for this wrapper in ``$HOME/bin``. Something to do with the first two lines in the MAKEFILE. The simplest solution I found is to just link this script to that location
.. [#f2] If you are using GCC to compile your code with CUDA you cannot use GCC versions >8.2. In which case you must compile a different version of GCC on your machine. An excellent resource on how to do is found here https://bobsteagall.com/2017/12/30/gcc-builder/
