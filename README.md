# Project Usage Documentation. #

# Introduction #

This is taken from the README file included in the package under the bin directory.  A more complete version is `MalGen` v0.9 Overview.pdf which is also included in the package


# Details #

Generating the data is a two step process.  First, the initial run has to take
place on a single node.  This generates a data file of compromised events and
it's associated metadata file.  In addition, state information is saved from the
Python session as INITIAL.txt.  This file is necessary for step 2.

The INITIAL.txt file must be made available to each node that is going to
generate the uncompromised synthetic data.  We scp the file to each node where
this is going to take place and run the data generation in parallel across the
nodes.

The second step, for historical reasons, generates multiple data files and their
associated metadata and then concatenates them into a single file.  The
original pieces are then deleted.  Originally, this was so that the code could
run on older hardware with less RAM.  Later versions of the code improved memory
handling and this is no longer necessary, but it has not been removed.

# Requirements #

`MalGen` is Python code, so it should be able to run on most platforms.  We have only tested it on Linux and it requires Python 2.4.4 or above (there is a bug in the datetime module with version 2.4.3 and older that can cause problems).  We have tested it using Python 2.4.4 and 2.5.2.