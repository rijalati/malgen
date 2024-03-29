#!/bin/bash

################################################################################
# env.sh
#
# Common definitions used in the supproting scripts for the MalGen project.  You
# can add -x to the shell declaration above to debug.  If you want to just to
# examine the values, you can run the test.sh file which has debugging enabled
# and sources this file.
################################################################################

## APPLICATIONS ##

# ssh is required.  This verifies that before anything is attempt.
SSH=`which ssh`
if [ -z "${SSH}" ]; then
    echo "$0 Cannot find ssh"; exit 1
fi

# scp is required.  This verifies that before anything is attempt.
SCP=`which scp`
if [ -z "${SCP}" ]; then
    echo "$0 Cannot find scp"; exit 1
fi

# Python is required.  This verifies that before anything is attempt.
# We have tested against Python 2.4.4
PYTHON=`which python`
if [ -z "${PYTHON}" ]; then
    echo "$0 Cannot find python"; exit 1
fi


## PARAMETERS **

# Configurable parameters.  These are guesses, you might have to modify these
# for your network.

# This should be your home directory on each machine where data is generated.
# Alternatively, it can be the install directory where the malgen files have
# been placed.
ME=`whoami`
MY_HOME=/home/${ME}

# ${MY_HOME}/${SCRIPTS_DIR} is where this file and test.sh lives as well as the
# execs, fork, and malgen directories.
SCRIPTS_DIR=bin/cloud

# Should live off of the SCRIPTS_DIR above. This is where malgen.py and
# malgen.sh are located.
MALGEN_HOME=malgen

# Install directories for the applications.  Make sure that this matches the
# Hadoop version that you are using
HADOOP_DIR=hadoop-0.18.3
SECTOR_DIR=codeblue2
HADOOP_INSTALL_DIR=${MY_HOME}/${HADOOP_DIR}
SECTOR_INSTALL_DIR=${MY_HOME}/${SECTOR_DIR}

# Location for the raw data files to be loaded into Hadoop and Sector.  This is
# on the local file system.  These files in here will be uploaded in the
# distributed file systems.
IMPORT_FILE_DIR=/raid/testdata

# Sector's data directory
# There is not one for Hadoop.  The path is probably something like /raid/hadoop
# but you never do anything with it explicitly during MalGen.
SECTOR_FS=/raid/sector/data

# Top-level directory where files are loaded into (off of the respective data
# directories).
HADOOP_FILE_DIR=testdata
SECTOR_FILE_DIR=testdata

# Components of the file name that is used for MalGen.
# The full name becomes events-malstone-<NODE>.dat
DATA_FILE_BASE=events-malstone
DATA_FILE_EXT=dat

# How many records the data file generated by the initial seed run contains.
INITIAL_BLOCK_SIZE=500000000

# How many iterations of malgen.py to perform on each node where data is
# generated.  For historical reasons, if you want to generate 500 million
# records per file, you would generate 5 files with 100000000 records each and
# they get concatenated.
NUM_BLOCKS=5

# How many records to generate at one time when generating the uncompromised
# data.  The data file for the node will have NUM_BLOCKS * BLOCK_SIZE records
BLOCK_SIZE=100000000
