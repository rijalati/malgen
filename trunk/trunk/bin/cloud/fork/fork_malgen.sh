#!/bin/bash

# load gloabl values for directory locations, etc
source ../env.sh

COMMAND=malgen.sh
for NODE in `cat ../nodes.txt`; do
    (${SSH} -2 ${NODE} \
        "cd ${MY_HOME}/${SCRIPTS_DIR}/${MALGEN_HOME}; ./${COMMAND}";)&
done;

exit 0

