# Takes arbitrary command line arguments
#   1) string; path to OBJ shirt model
#   2 and up) int; vertices to pin

# Generates files in the /dropped/ directory
#   1) an OBJ file called dropped_vtx.obj, where vtx is the vertex number
#   2) a Maya mb file called dropped_vtx.obj, where vtx is the vertex number

import sys
#sys.path.insert(0, "/Applications/Autodesk/maya2015/Maya.app/Contents/Frameworks/Python.framework/Versions/Current/lib/python2.7/site-packages")
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import os
import time

OSX_RENDER_DIR = "/Users/" + str(getpass.getuser()) + "/Documents/maya/projects/default/images/"
OSX_MB_DIR = "/Users/" + str(getpass.getuser()) + "/Documents/maya/projects/default/"
UBUNTU_RENDER_DIR = "/home/" + str(getpass.getuser()) + "/maya/projects/default/images/"
UBUNTU_MB_DIR = "/home/" + str(getpass.getuser()) + "/maya/projects/default/"

# System specific paths
RENDER_DEFAULT_DIRECTORY = OSX_RENDER_DIR
MB_DEFAULT_DIRECTORY = OSX_MB_DIR

OUT_NAME = "dropped"
STARTFRAME = 0
ENDFRAME = 300
VERTICES = []
for x in range(len(sys.argv)-2):
    VERTICES.append(int(sys.argv[x+2]))

# Import shirt, convert to nCloth
def to_nCloth():
    cmds.loadPlugin("objExport")
    mel.eval('file -f -options "mo=1" -ignoreVersion -typ "OBJ" -o "%s";' % sys.argv[1])
    cmds.select(clear = True)
    cmds.select("shirt")
    mel.eval("doCreateNCloth 0;")
# Pin vertices
def pin_vertex(vtx):
    """Takes in a vertex number"""
    shirt_vertex="shirt.vtx[" + str(vtx) + "]"
    cmds.select(clear = True)
    cmds.select(shirt_vertex)
    mel.eval("createNConstraint transform 1;")
# Drop Shirt model
def drop_simulation():
    start = time.time()
    cmds.playbackOptions(min = STARTFRAME, max = ENDFRAME)
    cmds.currentTime(STARTFRAME)
    cmds.select(clear = True)
    cmds.select("shirt")
    cmds.bakeResults(simulation = True, controlPoints = True, shape = True, time = (STARTFRAME, ENDFRAME))
    cmds.currentTime(ENDFRAME)
    end = time.time()
    return end-start
# Convert to OBJ
def export_obj(name):
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/dropped/" + name
    for x in VERTICES:
        obj_path += "_" + str(x)
    obj_path += ".obj"
    print("Saving file as " + obj_path)
    cmds.select(clear = True)
    cmds.select("shirt")
    mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "OBJexport" -pr -es "%s";' % obj_path)
# Export as Maya binary
def export_mb(name):
    obj_name = name
    for x in VERTICES:
        obj_name += "_" + str(x)
    obj_name += ".mb"
    cmds.file(rename = obj_name)
    cmds.file(save = True, type = "mayaBinary")
    os.system("cp " + OSX_MB_DEFAULT_DIRECTORY + obj_name + " " + os.path.dirname(os.path.realpath(__file__)) + "/dropped/" + obj_name)


# Main program
print("Running simulation on file " + sys.argv[1])
print("Simulation performed on vertices numbered " + str(VERTICES))
to_nCloth()
for x in VERTICES:
    pin_vertex(x)
time_elapsed = drop_simulation()
print("Simulation took " + str(time_elapsed) + " seconds to run")
export_obj(OUT_NAME)
export_mb(OUT_NAME)
