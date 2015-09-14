#!/bin/sh

some_cmd=`which maya`
path=`dirname $(readlink -f $some_cmd)`
pythonhome=$path/..
export PYTHONHOME=$pythonhome
export LD_LIBRARY_PATH=$path/../lib:$LD_LIBRARY_PATH
export MAYA_LOCATION=$path/..

some_cmd=`which maya`
path=`dirname $(readlink -f $some_cmd)`
pythonhome=`dirname $path`
pythonpath=$pythonhome/lib/python2.7/site-packages
export PATH=$path:$PATH
export PYTHONHOME=$pythonhome
export PYTHONPATH=$pythonpath:$PYTHONPATH
export LD_LIBRARY_PATH=$path/lib:$LD_LIBRARY_PATH
export MAYA_LOCATION=$path
export MAYA_NO_BUNDLE_RESOURCES=1

echo $PATH
echo $PYTHONHOME
echo $PYTHONPATH
echo $MAYA_LOCATION
echo $LD_LIBRARY_PATH
echo $MAYA_NO_BUNDLE_RESOURCES
`python`
#`python -vc "import sys; print sys.path"`
#`python -v "import maya.standalone; maya.standalone.initialize()"`
