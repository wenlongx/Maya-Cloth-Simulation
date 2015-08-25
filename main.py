# Takes 0 command line arguments
# User inputs two XYZ coordinates, which represent the point on the shirt to grasp, and the point which it is folded to

# Generates in the /folded/ directory
#   1) an IFF image called /images/shirtX.iff, where X is the fold number
#   2) a Maya binary called /snapshots/shirtX.mb, where X is the fold number
#   3) an OBJ file called /snapshots/shirtX.obj, where X is the fold number

import sys
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import os
import time
import math
import ntpath
import presets

# Correct Version
if sys.version_info[0] >= 3:
    get_input = input
else:
    get_input = raw_input

TABLE_SIZE = 20.0
OUT_NAME = "folded"
HEIGHT = 2
MOVE_SPEED = (30/100.0)
SETTLE_TIME = 100
RETRACT_HEIGHT = 5

# main function
def start():
    # Manual Input of Points
    # Enter XYZ points, converted to vertices
    print("Running folding simulation on file " + sys.argv[1])
    print("This simulation folds the input cloth from point A to point B, and saves the resulting file as an OBJ. You may specify multiple folds, by entering multiple pairs of points.")
    print("~~~")
    print("Enter points in the form of X,Y,Z coordinates (Ex: 1,2,3). Enter \"quit\" to begin the folding simulation with the given points")

    global fold_num
    fold_num = 0

    global not_first
    not_first = False

    # take in points
    while(True):
        coords = []
        vertices = []
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
            # Set up Scene
            if (fold_num == 0):
                import_shirt()
            else:
                import_shirt("folded/snapshots/shirt" + str(fold_num) + ".obj")
            create_camera()
            create_table()

            coords.append(temp)
            coords.append([int(x.strip()) for x in p.split(',')])
            for c in coords:
                vertices.append(XYZ_to_vtx(c))

            # Fold the shirt
            global fold_num
            fold(fold_num+1, vertices[0], vertices[1])
            fold_num += 1

# setup functions
# TODO - all checked off
def import_shirt(name=sys.argv[1]):
    # imports shirt, scales to fit, converts to ncloth
    cmds.loadPlugin("objExport")
    mel.eval('file -f -options "mo=1" -ignoreVersion -typ "OBJ" -o "%s";' \
         % name)
    # scale shirt to fit
    if (fold_num == 0):
        bbx = cmds.xform("shirt", q=True, bb=True, ws=True)
        s_x_len = abs(bbx[3] - bbx[0])
        s_y_len = abs(bbx[4] - bbx[1])
        if (s_x_len >= s_y_len):
            scale = 0.8 * TABLE_SIZE/s_x_len
        else:
            scale = 0.8 * TABLE_SIZE/s_y_len
        cmds.scale(scale, scale, scale, "shirt", centerPivot = True)
    shirt_to_nCloth()
def shirt_to_nCloth():
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
def create_table():
    # Create a table mesh that collides with nCloth
    cmds.polyPlane(name = "table", w = TABLE_SIZE, h = TABLE_SIZE)
    cmds.select(clear = True)
    # table material settings
    mel.eval('select -r table;')
    mel.eval('shadingNode -asShader lambert;')
    mel.eval('rename lambert2 "table_mat";')
    mel.eval('sets -renderable true -noSurfaceShader true' + \
        '-empty -name -table_matSG;')
    mel.eval('connectAttr -f table_mat.outColor table_matSG.surfaceShader;')
    mel.eval('setAttr "table_mat.color" -type double3 0 0 0;')
    mel.eval('setAttr "table_mat.ambientColor" -type double3 0 0 0;')
    mel.eval('select -r table ; sets -e -forceElement table_matSG;')
    cmds.select("table")
    cmds.move(0, -0.001, 0, relative = True)
    mel.eval("makeCollideNCloth")
def create_camera():
    # creates a camera
    mel.eval('camera -centerOfInterest 5 -focalLength 35 -cameraScale 1;objectMoveCommand; cameraMakeNode 2 "";')
    mel.eval('select -r camera1_aim; move -absolute -worldSpaceDistance 0 0 0;')
    mel.eval('select -r camera1; move -absolute -worldSpaceDistance 0 5 0;')
    cmds.viewFit('camera1', all=True)
    cmds.select(clear=True)
    cmds.select("camera1")
    # render settings
    mel.eval('setAttr "frontShape.renderable" 0;')
    mel.eval('setAttr "topShape.renderable" 0;')
    mel.eval('setAttr "sideShape.renderable" 0;')
    mel.eval('setAttr "perspShape.renderable" 0;')
    mel.eval('setAttr "cameraShape1.renderable" 1;')
    prep_render()
def prep_render():
    # shirt material settings
    mel.eval('select -r shirt;')
    mel.eval('shadingNode -asShader lambert;')
    mel.eval('rename lambert2 "shirt_mat";')
    mel.eval('sets -renderable true -noSurfaceShader true' + \
        '-empty -name -shirt_matSG;')
    mel.eval('connectAttr -f shirt_mat.outColor shirt_matSG.surfaceShader;')
    mel.eval('setAttr "shirt_mat.color" -type double3 1 1 1;')
    mel.eval('setAttr "shirt_mat.ambientColor" -type double3 1 1 1;')
    mel.eval('select -r shirt ; sets -e -forceElement shirt_matSG;')
    # pointer material settings
    mel.eval('shadingNode -asShader lambert;')
    mel.eval('rename lambert2 "pointer_mat";')
    mel.eval('sets -renderable true -noSurfaceShader true' + \
        '-empty -name -pointer_matSG;')
    mel.eval('connectAttr -f pointer_mat.outColor pointer_matSG.surfaceShader;')
    mel.eval('setAttr "pointer_mat.transparency" -type double3 1 1 1;')

# helper functions
def XYZ_to_vtx(coordinate):
    # takes in coordinate [x,y,z] and returns the minimum distance
    min_dist = -1
    min_vtx = 0
    cmds.select("shirt")
    num_points = cmds.polyEvaluate(v=True)
    for n in range(num_points):
        v = get_position('shirt.vtx[' + str(n) + ']')
        dist = math.sqrt((coordinate[0]-v[0])**2 + (coordinate[2]-v[2])**2)
        if (min_dist < 0):
            min_dist = dist
            min_vtx = n
        if (min_dist > dist):
            min_dist = dist
            min_vtx = n
    return min_vtx
def get_position(vtx_string):
    # Gets the global position of a vertex
    # Input is a string of the form: "shirt.vtx[2]", or "table.vtx[36]"
    pos = mel.eval("xform -ws -q -t " + vtx_string + " ;")
    return pos
def bake(start, end):
    # Baking fold animation keyframes
    om.MGlobal.viewFrame(start)
    cmds.select("shirt")
    cmds.bakeResults(simulation=True, controlPoints=True, shape=True, time=(start, end))
def render_frame(out):
    mel.eval('render -x 500 -y 500 camera1;')
    name = "shirt" + out
    os.system("sudo mv /private/var/root/Documents/maya/projects/default/images/" + name + ".iff " + os.path.dirname(os.path.realpath(__file__)) + "/folded/images/" + name + ".iff")

# export functions
def export_mb(name):
    cmds.file(rename = name + ".mb")
    cmds.file(save = True, type = "mayaBinary")
    os.system("cp /private/var/root/Documents/maya/projects/default/" + name + \
        ".mb " + os.path.dirname(os.path.realpath(__file__)) + "/folded/snapshots/" + name + ".mb")
def export_obj(name):
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/folded/snapshots/" + name + ".obj"
    print("Saving file as " + obj_path)
    om.MGlobal.viewFrame(mel.eval('playbackOptions -query -max'))
    cmds.select(clear=True)
    cmds.select("shirt")
    mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "OBJexport" -pr -es "%s";' % obj_path)

# fold functions
def create_pointer():
    # Create a pointer mesh that represents the robot claw
    cmds.polyCone(name="pointer", sx=3, r=0.5, h=2)
    cmds.select(clear=True)
    cmds.select("pointer")
    mel.eval('select -r pointer ; sets -e -forceElement pointer_matSG;')
    cmds.select("pointer")
    cmds.rotate("180deg", 0, 0, r=True)
    cmds.move(0, -1, 0, "pointer.scalePivot", "pointer.rotatePivot")
    cmds.move(0, 1, 0, absolute=True)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1)
    mel.eval("makeCollideNCloth")
def bind_pointer(vtx):
    cmds.select(clear=True)
    mel.eval('select -r shirt.vtx[' + str(vtx) + '];')
    mel.eval('select -tgl pointer; createNConstraint transform 0;')
    mel.eval('select -r dynamicConstraint1;')
    mel.eval('select -add pointer; Parent;')
    mel.eval('setAttr \"dynamicConstraintShape1.glueStrength\" 0;')
    mel.eval('setKeyframe -t 0 { \"dynamicConstraintShape1.gls\" };')
    mel.eval('setAttr \"dynamicConstraintShape1.glueStrength\" 1;')
    mel.eval('setKeyframe -t 1 { \"dynamicConstraintShape1.gls\" };')
def release_pointer(time):
    cmds.select(clear=True)
    mel.eval('select -tgl pointer;')
    mel.eval('setKeyframe -t ' + str(time) + ' { \"dynamicConstraintShape1.gls\" };')
    mel.eval('setAttr \"dynamicConstraintShape1.glueStrength\" 0;')
    mel.eval('setKeyframe -t ' + str(time+1) + ' { \"dynamicConstraintShape1.gls\" };')
def move_pointer(x, y, z):
    cmds.select("pointer")
    cmds.move(x, y, z, absolute=True, worldSpace=True, worldSpaceDistance=True)
def fold(n, A, B, STARTFRAME = 0):
    # A, B are the vertices
    # n is the fold #
    # STARTFRAME is the frame at which the current fold starts
    # Set constants
    vtx1 = get_position("shirt.vtx[" + str(A) + "]")
    vtx2 = get_position("shirt.vtx[" + str(B) + "]")
    
    time1 = STARTFRAME
    time2 = int(HEIGHT/MOVE_SPEED)
    time3 = int(math.hypot((vtx2[0]-vtx1[0]),(vtx2[2]-vtx1[2]))/MOVE_SPEED)
    time4 = int(HEIGHT/MOVE_SPEED)
    
    ENDFRAME = time1 + time2 + time3 + time4 + SETTLE_TIME
    cmds.playbackOptions(min = STARTFRAME)
    cmds.playbackOptions(max = ENDFRAME)

    # Movement
    create_pointer()
    move_pointer(vtx1[0], vtx1[1], vtx1[2])
    bind_pointer(A)
    cmds.select(clear=True)
    cmds.select("pointer")
    cmds.setKeyframe(t=time1)
    move_pointer(vtx1[0], vtx1[1]+HEIGHT, vtx1[2])
    cmds.setKeyframe(t=time1+time2)
    move_pointer(vtx2[0], vtx1[1]+HEIGHT, vtx2[2])
    cmds.setKeyframe(t=time1+time2+time3)
    vtx2 = get_position("shirt.vtx[" + str(B) + "]")
    move_pointer(vtx2[0], vtx2[1], vtx2[2])
    release_pointer(time1+time2+time3+time4)
    cmds.setKeyframe(t=time1+time2+time3+time4)
    move_pointer(vtx2[0], RETRACT_HEIGHT, vtx2[2])
    cmds.setKeyframe(t=time1+time2+time3+time4+SETTLE_TIME)

    bake(STARTFRAME,ENDFRAME)
    om.MGlobal.viewFrame(ENDFRAME)
    export_obj("shirt" + str(n))
    export_mb("shirt" + str(n))
    render_frame(str(n))

# Main program

start()





