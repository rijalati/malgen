#!/bin/bash

# load gloabl values for directory locations, etc
source ../env.sh

if [ $# != 2 ]; then
    echo "$0 takes two parameters."
    echo "    $0 <MASTER_IP> <MASTER_PORT>";
    exit 1;
fi

# Even if you are going across mulitple clusters,
# there is only one master node and ip.
MASTER_IP=$1
MASTER_PORT=$2


COMMAND=exec_upload.sh

for NODE in `cat ../nodes.txt`; do
    (${SSH} -2 ${NODE} \
        "cd ${MY_HOME}/${SCRIPTS_DIR}/execs; ./${COMMAND} ${MASTER_IP} ${MASTER_PORT} ${NODE}";)&
done;

exit 0

