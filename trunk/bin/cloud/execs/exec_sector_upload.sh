#!/bin/bash

# load gloabl values for directory locations, etc
source ../env.sh

if [ $# != 3 ]; then
    echo "$0 takes three parameters."
    echo "    $0 <MASTER_IP> <MASTER_PORT> <HOST>";
    exit 1;
fi

# Passed in parameters
MASTER_IP=$1
MASTER_PORT=$2
HOST=$3

COMMAND=upload
cd ${SECTOR_INSTALL_DIR}/client
./${COMMAND} ${MASTER_IP} ${MASTER_PORT} ${IMPORT_FILE_DIR}/${DATA_FILE_BASE}-${CLUSTER}.${DATA_FILE_EXT} ${SECTOR_FILE_DIR}/${DATA_FILE_BASE}-${CLUSTER}.${DATA_FILE_EXT}

