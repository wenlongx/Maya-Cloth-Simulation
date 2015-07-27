# Takes arbitrary command line arguments
#   1) string; path to OBJ shirt model
#   2 and up) int; vertices to pin

# Generates an OBJ file in the current directory
#   1) an OBJ file called out_vtx.obj, where vtx is the vertex number

import sys
#sys.path.insert(0, "/Applications/Autodesk/maya2015/Maya.app/Contents/Frameworks/Python.framework/Versions/Current/lib/python2.7/site-packages")
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import os
import time

OUT_NAME = "out"
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
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/out/" + name
    for x in VERTICES:
        obj_path += "_" + str(x)
    obj_path += ".obj"
    print("Saving file as " + obj_path)
    cmds.select(clear = True)
    cmds.select("shirt")
    mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "OBJexport" -pr -es "%s";' % obj_path)


# Main program
print("Running simulation on file " + sys.argv[1])
print("Simulation performed on vertices numbered " + str(VERTICES))
to_nCloth()
for x in VERTICES:
    pin_vertex(x)
time_elapsed = drop_simulation()
print("Simulation took " + str(time_elapsed) + " seconds to run")
export_obj(OUT_NAME)


'''
# Save a Maya Binary for Reference
cmds.file(rename = "out_2.mb")
cmds.file(save = True, type = "mayaBinary")
os.system("cp /private/var/root/Documents/maya/projects/default/out_2.mb ~/Desktop/out_2.mb")
'''
