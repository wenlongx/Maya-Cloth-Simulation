# Takes 3 command line arguments
#   1) string; path to OBJ shirt model
#   2) int; vertex to move
#   3) int; target vertex

# Generates files in the folded/ directory
#   1) an OBJ file called folded_vtx1_vtx2.obj, where vtx1 is the moved 
#       vertex and vtx2 is the target vertex
#   2) a Maya Binary file called folded_vtx_vtx2.mb, where vtx1 is the moved
#       vertex and vtx2 is the target vertex

import sys
#sys.path.insert(0, "/Applications/Autodesk/maya2015/Maya.app/Contents/Frameworks/Python.framework/Versions/Current/lib/python2.7/site-packages")
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import os
import time
import math
import presets

OUT_NAME = "folded"
VERTICES = []
HEIGHT = 1.0
MOVE_SPEED = (5.0/100.0)
SETTLE_TIME = 50

STARTFRAME = 1
ENDFRAME = 10

# Create a pointer mesh that represents the robot claw
def create_pointer():
    cmds.polyCone(name="pointer", sx=3, r=0.5, h=2)
    cmds.select(clear=True)
    cmds.select("pointer")
    cmds.rotate("180deg", 0, 0, r=True)
    cmds.move(0, -1, 0, "pointer.scalePivot", "pointer.rotatePivot")
    cmds.move(0, 1, 0, absolute=True)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1)
    mel.eval("makeCollideNCloth")


# Import shirt, convert to nCloth
def shirt_to_nCloth():
    cmds.loadPlugin("objExport")
    mel.eval('file -f -options "mo=1" -ignoreVersion -typ "OBJ" -o "%s";' \
         % sys.argv[1])
    cmds.select(clear=True)
    cmds.select("shirt")
    mel.eval("doCreateNCloth 0;")
    mel.eval('setAttr "nClothShape1.thickness" 0.001;')
    mel.eval('setAttr "nClothShape1.selfCollideWidthScale" 0.001;')

    # Different material presets
    presets.burlap()
    # presets.heavy_denim()
    # presets.loose_thick_knit()
    # presets.silk()
    # presets.thick_leather()
    # presets.tshirt()


# Create a table mesh that collides with nCloth
def create_table():
    cmds.polyPlane(name="table", w=15, h=15)
    cmds.select(clear=True)
    cmds.select("table")
    cmds.move(0, -0.001, 0, relative=True)
    mel.eval("makeCollideNCloth")


# "Grabs" a vertex by constraining pointer to vertex
# Make sure the pointer and vertex are in the same position to begin with
def bind_pointer():
    cmds.select(clear=True)
    mel.eval('select -r shirt.vtx[' + str(VERTICES[0]) + '] ; select ' + \
        '-tgl pointer ; createNConstraint transform 0;')
    mel.eval('select -r dynamicConstraint1; select -add pointer; Parent;')
    mel.eval('setKeyframe { "dynamicConstraintShape1.gls" };')


# "Lets go" of a vertex by unconstraining pointer/vertex
def release_pointer():
    mel.eval('setKeyframe { "dynamicConstraintShape1.gls" };')
    temp = cmds.currentTime(query=True)
    cmds.currentTime(temp+1)
    mel.eval('setAttr "dynamicConstraintShape1.glueStrength" 0;')
    mel.eval('setKeyframe { "dynamicConstraintShape1.gls" };')


# Gets the global position of a vertex
# Input is a string of the form: "shirt.vtx[2]", or "table.vtx[36]"
def get_position(vtx_string):
    pos = mel.eval("xform -ws -q -t " + vtx_string + " ;")
    return pos


# Move pointer to location
# Input is an int which refers the the shirt vertex
def move_pointer(x, y, z):
    cmds.select("pointer")
    cmds.move(x, y, z, absolute=True, worldSpace=True, worldSpaceDistance=True)


# Fold from vertex 1 to vertex 2
def fold():
    # Set constants
    vtx1 = get_position("shirt.vtx[" + str(VERTICES[0]) + "]")
    vtx2 = get_position("shirt.vtx[" + str(VERTICES[1]) + "]")
    
    time1 = 0
    time2 = int(HEIGHT/MOVE_SPEED)
    time3 = int(math.hypot((vtx2[0]-vtx1[0]),(vtx2[2]-vtx1[2]))/MOVE_SPEED)
    time4 = int(HEIGHT/MOVE_SPEED)
    
    STARTFRAME = 0
    ENDFRAME = time1 + time2 + time3 + time4 + SETTLE_TIME
    cmds.playbackOptions(min = STARTFRAME, max = ENDFRAME)

    # Movement
    cmds.currentTime(time1)
    move_pointer(vtx1[0], vtx1[1], vtx1[2])
    bind_pointer()
    cmds.select(clear=True)
    cmds.select("pointer")
    cmds.setKeyframe()
    
    cmds.currentTime(time1 + time2)
    move_pointer(vtx1[0], vtx1[1]+HEIGHT, vtx1[2])
    cmds.setKeyframe()

    cmds.currentTime(time1 + time2 + time3)
    move_pointer(vtx2[0], vtx1[1]+HEIGHT, vtx2[2])
    cmds.setKeyframe()
    
    vtx2 = get_position("shirt.vtx[" + str(VERTICES[1]) + "]")
    cmds.currentTime(time1 + time2 + time3 + time4)
    move_pointer(vtx2[0], vtx2[1], vtx2[2])
    cmds.setKeyframe()
    
    cmds.currentTime(time1 + time2 + time3 + time4 + SETTLE_TIME/3) 
    release_pointer()
    
    # Baking fold animation keyframes
    cmds.currentTime(0)
    cmds.select("shirt")
    cmds.bakeResults(simulation=True, controlPoints=True, shape=True, \
        time=(STARTFRAME, ENDFRAME))


# Convert to OBJ
def export_obj(name):
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/folded/" + name
    for x in VERTICES:
        obj_path += "_" + str(x)
    obj_path += ".obj"
    print("Saving file as " + obj_path)
    cmds.currentTime(mel.eval('playbackOptions -query -max'))
    cmds.select(clear=True)
    cmds.select("shirt")
    mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "OBJexport" -pr -es "%s";' % obj_path)

# Input Vertices, define Constants
for x in range(len(sys.argv)-2):
    VERTICES.append(int(sys.argv[x+2]))

# Main program
start = time.time()
print("Running folding simulation on file " + sys.argv[1])
print("Folding vertex " + str(VERTICES[0]) + " to vertex " + str(VERTICES[1]))
shirt_to_nCloth()
create_table()
create_pointer()
fold()
end = time.time()
print("Simulation took " + str(end-start) + " seconds to run")

# Saves a Maya binary, as well as an OBJ of just the shirt
export_obj(OUT_NAME)
cmds.file(rename = OUT_NAME + ".mb")
cmds.file(save = True, type = "mayaBinary")
os.system("cp /private/var/root/Documents/maya/projects/default/" + OUT_NAME + \
    ".mb " + os.path.dirname(os.path.realpath(__file__)) + "/folded/" + OUT_NAME + ".mb")


# Alternate bind_pointer
'''
def bind_pointer():
    cmds.select(clear=True)
    mel.eval('select -r shirt.vtx[' + str(VERTICES[0]) + '] ; select -tgl pointer ; createNConstraint pointToPoint 1;')
'''
