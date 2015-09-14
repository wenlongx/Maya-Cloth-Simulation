#!/bin/sh

some_cmd=`which maya`
path=`dirname $(readlink -f $some_cmd)`
pythonhome=$path/..
export PYTHONPATH=$PYTHONPATH:$pythonhome/lib/python2.7/site-packages
export PYTHONHOME=$pythonhome
export LD_LIBRARY_PATH=$path/../lib:$LD_LIBRARY_PATH
export MAYA_LOCATION=$path/..

exec $path/python-bin "$@"

