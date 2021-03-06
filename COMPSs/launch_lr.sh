#!/bin/bash

enqueue_compss \
  --exec_time=15 \
  --num_nodes=3 \
  --tasks_per_node=16 \
  --master_working_dir=. \
  --worker_working_dir=scratch \
  --lang=python \
  --pythonpath=/gpfs/home/bsc19/bsc19565/COMPSs/ \
  --classpath=/gpfs/home/bsc19/bsc19565/COMPSs/ \
  --comm="integratedtoolkit.nio.master.NIOAdaptor" \
  --tracing=true \
  --graph=true \
  /gpfs/home/bsc19/bsc19565/COMPSs/lr.py $1 $2 $3 

#  numP
#  dim
#  numFrag
