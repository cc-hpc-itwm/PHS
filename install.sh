#!/bin/bash

# The purpose of this script is to append the absolute path of this script (DIR)
# to the module search paths (where python looks for modules) using the 'import'
# command in python.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Instead of manipulating the environment variable PYTHONPATH it is possible to
# create a path configuration file
# First we have to find out where python searches for these .pth files:
SITEDIR=$(python -m site --user-site)
# create if it doesn't exist
mkdir -p "$SITEDIR"
# create new .pth file with our path
echo "$DIR" > "$SITEDIR/parallel_hyperparameter_search.pth"
