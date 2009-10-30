#!/bin/bash

# This could take a long time if you have a lot of nodes.  We supply it just in
# case, but it might be better if the file is copied to a single directory that
# is viabale to each node.

# The location of INITIAL.txt must be passed in on the command line.  For
# example:
#     ./pushout_initial.sh /tmp/INITIAL.txt

# load gloabl values for directory locations, etc^
source ../env.sh

# The generted INITIAL.txt
FILE=$1
if [ -z ${FILE} ]; then
    echo "$0 requires the path to INITIAL.txt as a parameter.";
    echo "    $0 /tmp/INITIAL.txt";
    exit 1;
fi

for NODE in `cat ../nodes.txt`; do
    ${SCP} ${FILE} ${NODE}:${IMPORT_FILE_DIR}/
done;

exit 0;

