==============
Running
==============

MPI
====

To run your scripts with MPI (i.e. procs only)

.. code-block:: bash

   mpirun -np 56 lmp_kokkos_cuda_mpi \

If you are using SLURM as your job manager use

.. code-block:: bash

   mpirun -np $SLURM_NTASKS lmp_kokkos_cuda_mpi \


KOKKOS
=======

To run your scripts in parallel with using KOKKOS and 1 GPU use:

.. code-block:: bash

   mpirun -np 1 lmp_kokkos_cuda_mpi \
   -k on g 1 -sf kk -pk kokkos neigh half neigh/qeq full newton on \

You must use only **one** MPI process for **one** GPU