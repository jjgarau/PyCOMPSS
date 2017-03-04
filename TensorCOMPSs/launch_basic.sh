#!/bin/bash

enqueue_compss \
  --exec_time=5 \
  --num_nodes=2 \
  --tasks_per_node=16 \
  --master_working_dir=. \
  --worker_working_dir=scratch \
  --lang=python \
  --pythonpath=/gpfs/home/bsc19/bsc19565/TensorCOMPSs/ \
  --classpath=/gpfs/home/bsc19/bsc19565/TensorCOMPSs/ \
  --comm="integratedtoolkit.nio.master.NIOAdaptor" \
  --graph=true \
  --tracing=true \
  /gpfs/home/bsc19/bsc19565/TensorCOMPSs/basic_operations_compss.py $1

#  numFrag = numero de fragments 
