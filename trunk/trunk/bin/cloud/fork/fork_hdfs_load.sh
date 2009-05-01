#!/bin/bash

# load gloabl values for directory locations, etc
source ../env.sh

COMMAND=bin/hadoop
for NODE in `cat ../nodes.txt`; do
    (${SSH} -2 ${NODE} \
        "cd ${HADOOP_INSTALL_DIR}; ./${COMMAND} dfs -put \
            ${IMPORT_FILE_DIR}/${DATA_FILE_BASE}-${NODE}.${DATA_FILE_EXT} ${HADOOP_FILE_DIR}/${DATA_FILE_BASE}-${NODE}.${DATA_FILE_EXT}";)&
done;

exit 0
