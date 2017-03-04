#!/bin/bash

enqueue_compss \
  --exec_time=60 \
  --num_nodes=2 \
  --tasks_per_node=16 \
  --master_working_dir=. \
  --worker_working_dir=scratch \
  --lang=python \
  --pythonpath=/gpfs/home/bsc19/bsc19565/TensorCOMPSs/ \
  --classpath=/gpfs/home/bsc19/bsc19565/TensorCOMPSs/ \
  --comm="integratedtoolkit.nio.master.NIOAdaptor" \
  --graph=true \
  --debug=false \
  /gpfs/home/bsc19/bsc19565/TensorCOMPSs/kmTC_2.py $1 $2 $3 $4

# numP
# dim
# k
#  numFrag = numero de fragments 
