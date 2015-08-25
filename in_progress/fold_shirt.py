# Takes 3 command line arguments
#   1) string; path to OBJ shirt model

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

# Correct Version
if sys.version_info[0] >= 3:
    get_input = input
else:
    get_input = raw_input

TABLE_SIZE = 20.0
OUT_NAME = "folded"
HEIGHT = 1.0
MOVE_SPEED = (5.0/100.0)
SETTLE_TIME = 50
RETRACT_HEIGHT = 5

VERTICES = []
# Coordinates in X,Y,Z
C = []

def start():
    # Main program
    start = time.time() 

    # Setup
    shirt_to_nCloth()
    create_table()
    
    # Manual Input of Points
    # Enter XYZ points, converted to vertices
    if (len(sys.argv) < 3):
        print("Running folding simulation on file " + sys.argv[1])
        print("This simulation folds the input cloth from point A to point B, and saves the resulting file as an OBJ. You may specify multiple folds, by entering multiple pairs of points.")
        print("~~~")
        print("Enter points in the form of X,Y,Z coordinates (Ex: 1,2,3). Enter \"quit\" to begin the folding simulation with the given points")

        # C contains tuples of XYZ points
        # C = [ [0,0,0]
        #       [2,2,2]
        #       [2,1,2]
        #       [1,0,0] ]
        # in this case, [0,0,0] would fold to [2,2,2] and [2,1,2] folds to [1,0,0]
        while(True):
            print("Enter two points:")
            p = get_input("  Enter 1st point: ")
            if (p[0].upper() == 'Q'):
                break
            else:
                temp = [int(x.strip()) for x in p.split(',')]
            p = get_input("  Enter 2nd point: ")
            if (p[0].upper() == 'Q'):
                break
            else:
                C.append(temp)
                C.append([int(x.strip()) for x in p.split(',')])

        cmds.select("shirt")
        num_points = cmds.polyEvaluate(v=True)
        min_val = dict()
        # min_val is a dictionary that uses an XYZ tuple as a key
        #   and holds a tuple of [dist, n], where distance is the distance
        #   between XYZ coord and a given vertex, and n is the vertex number.
        #   This dictionary lets us find the vertex number given the XYZ coords.
        for n in range(num_points):
            v = get_position('shirt.vtx[' + str(n) + ']')
            for c in C:
                dist = math.sqrt((c[0]-v[0])**2 + (c[1]-v[1])**2 + (c[2]-v[2])**2)
                if (str(c) in min_val):
                    if (dist < min_val[str(c)][0]):
                        min_val[str(c)] = [dist, n]
                else:
                    min_val[str(c)] = [dist, n]
        
        print("The points you entered were matched to the vertices:")
        for c in C:
            print("Vertex " + str(min_val[str(c)][1]) + " corresponds to X,Y,Z coordinate " + str(c))

    # Fold the shirt
    next_frame = 0
    for x in range(len(C)/2):
        create_pointer(x+1)
        next_frame = fold(min_val[str(C[x])][1], min_val[str(C[x+1])][1], x+1, next_frame)
    #bake(next_frame)
    end = time.time()
    print("Simulation took " + str(end-start) + " seconds to run")



# Create a pointer mesh that represents the robot claw
def create_pointer(n):
    cmds.polyCone(name="pointer"+str(n), sx=3, r=0.5, h=2)
    cmds.select(clear=True)
    cmds.select("pointer"+str(n))
    cmds.rotate("180deg", 0, 0, r=True)
    cmds.move(0, -1, 0, "pointer" + str(n) + ".scalePivot", "pointer" + str(n) + ".rotatePivot")
    cmds.move(0, 1, 0, absolute=True)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1)
    mel.eval("makeCollideNCloth")


# Import shirt, convert to nCloth
def shirt_to_nCloth():
    cmds.loadPlugin("objExport")
    mel.eval('file -f -options "mo=1" -ignoreVersion -typ "OBJ" -o "%s";' \
         % sys.argv[1])
    
    # scale shirt to fit
    bbx = cmds.xform("shirt", q=True, bb=True, ws=True)
    s_x_len = bbx[3] - bbx[0]
    s_y_len = bbx[4] - bbx[1]
    if (s_x_len >= s_y_len):
        scale = 0.8 * TABLE_SIZE/s_x_len
    else:
        scale = 0.8 * TABLE_SIZE/s_y_len
    cmds.scale(scale, scale, scale, "shirt", centerPivot = True)
    
    # convert shirt to nCloth
    cmds.select(clear=True)
    cmds.select("shirt")
    mel.eval("doCreateNCloth 0;")
    mel.eval('setAttr "nClothShape1.thickness" 0.001;')
    mel.eval('setAttr "nClothShape1.selfCollideWidthScale" 0.001;')

    # Different material presets
    presets.custom_shirt_cloth()
    # presets.burlap()
    # presets.heavy_denim()
    # presets.loose_thick_knit()
    # presets.silk()
    # presets.thick_leather()
    # presets.tshirt()


# Create a table mesh that collides with nCloth
def create_table():
    cmds.polyPlane(name = "table", w = TABLE_SIZE, h = TABLE_SIZE)
    cmds.select(clear = True)
    cmds.select("table")
    cmds.move(0, -0.001, 0, relative = True)
    mel.eval("makeCollideNCloth")


def bind_pointer(vtx, n):
    cmds.select(clear=True)
    mel.eval('select -r shirt.vtx[' + str(vtx) + '];')
    mel.eval('select -tgl pointer' + str(n) + '; createNConstraint transform 0;')
    mel.eval('select -r dynamicConstraint' + str(n) + ';')
    mel.eval('select -add pointer' + str(n) + '; Parent;')
    #mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 0;')
    #mel.eval('setKeyframe { \"dynamicConstraintShape' + str(n) + '.gls\" };')
    #temp = cmds.currentTime(query=True)
    #cmds.currentTime(temp+1)
    mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 1;')
    mel.eval('setKeyframe { \"dynamicConstraintShape' + str(n) + '.gls\" };')

def release_pointer(n):
    cmds.select(clear=True)
    mel.eval('select -tgl pointer' + str(n))
    mel.eval('setKeyframe { \"dynamicConstraintShape' + str(n) + '.gls\" };')
    temp = cmds.currentTime(query=True)
    cmds.currentTime(temp+1)
    mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 0;')
    mel.eval('setKeyframe { \"dynamicConstraintShape' + str(n) + '.gls\" };')


# Gets the global position of a vertex
# Input is a string of the form: "shirt.vtx[2]", or "table.vtx[36]"
def get_position(vtx_string):
    pos = mel.eval("xform -ws -q -t " + vtx_string + " ;")
    return pos


# Move pointer to location
# Input is an int which refers the the shirt vertex
def move_pointer(x, y, z, n):
    cmds.select("pointer" + str(n))
    cmds.move(x, y, z, absolute=True, worldSpace=True, worldSpaceDistance=True)


# Fold from vertex 1 to vertex 2
# A and B are in the form 
def fold(A, B, n, STARTFRAME = 0):
    # Set constants
    vtx1 = get_position("shirt.vtx[" + str(A) + "]")
    vtx2 = get_position("shirt.vtx[" + str(B) + "]")
    
    time1 = STARTFRAME
    time2 = int(HEIGHT/MOVE_SPEED)
    time3 = int(math.hypot((vtx2[0]-vtx1[0]),(vtx2[2]-vtx1[2]))/MOVE_SPEED)
    time4 = int(HEIGHT/MOVE_SPEED)
    
    ENDFRAME = time1 + time2 + time3 + time4 + SETTLE_TIME
    cmds.playbackOptions(min = STARTFRAME, max = ENDFRAME)
    
    # Movement
    cmds.currentTime(time1)
    move_pointer(vtx1[0], vtx1[1], vtx1[2], n)
    bind_pointer(A, n)
    cmds.select(clear=True)
    cmds.select("pointer" + str(n))
    cmds.setKeyframe()
    cmds.currentTime(time1 + time2)
    move_pointer(vtx1[0], vtx1[1]+HEIGHT, vtx1[2], n)
    cmds.setKeyframe()
    cmds.currentTime(time1 + time2 + time3)
    move_pointer(vtx2[0], vtx1[1]+HEIGHT, vtx2[2], n)
    cmds.setKeyframe()
    vtx2 = get_position("shirt.vtx[" + str(B) + "]")
    cmds.currentTime(time1 + time2 + time3 + time4)
    move_pointer(vtx2[0], vtx2[1], vtx2[2], n)
    release_pointer(n)
    cmds.setKeyframe()
    cmds.currentTime(time1 + time2 + time3 + time4 + SETTLE_TIME)
    move_pointer(vtx2[0], RETRACT_HEIGHT, vtx2[2], n)
    cmds.setKeyframe()
    return ENDFRAME


def bake(end):
    # Baking fold animation keyframes
    cmds.currentTime(0)
    cmds.select("shirt")
    cmds.bakeSimulation(simulation=True, controlPoints=True, shape=True, time=(0, end))
    

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


# Main Program
# Input Vertices, define Constants
for x in range(len(sys.argv)-2):
    VERTICES.append(int(sys.argv[x+2]))

start()
# Saves a Maya binary, as well as an OBJ of just the shirt
#export_obj(OUT_NAME)
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
'''
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
'''
