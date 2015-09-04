# Takes 1 mandatory and 1 optional command line argument
# User inputs two XYZ coordinates, which represent the point on the shirt to grasp, and the point which it is folded to
#   1) mandatory: OBJ file which provides the model to fold
#   2) optional: CSV file which provides the control points (key points used to create the model), to track

# Generates in the /folded/ directory
#   1) an IFF image called /images/shirtX.iff, where X is the fold number
#   2) a Maya binary called /snapshots/shirtX.mb, where X is the fold number
#   3) an OBJ file called /snapshots/shirtX.obj, where X is the fold number
# Conditional Outputs:
#   4) if the variable STEPS is greater than 1, OBJ files called /snapshots/shirtX_Y.obj, where X is the fold number and Y is the sub-step
#   5) if a CSV file is provided, CSV files called /snapshots/shirtX.csv or /snapshots/shirtX_Y.csv for all obj models
# Other Outputs:
#   1) files called cacheX.xml, where X is the fold number, are generated in /cache/. These files should not be edited/removed. They're used in the Maya binary files to record the simulation of the shirt being folded.

# Mac OSX Mayapy path
# /Applications/Autodesk/maya2015/Maya.app/Contents/bin/mayapy
# Ubuntu Mayapy path
# /usr/autodesk/maya2015-x64/bin/mayapy


OSX_RENDER_DIR = "/private/var/root/Documents/maya/projects/default/images/"
OSX_MB_DIR = "/private/var/root/Documents/maya/projects/default/"
UBUNTU_RENDER_DIR = ""
UBUNTU_MB_DIR = ""

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
import csv

# Correct Version
if sys.version_info[0] >= 3:
    get_input = input
else:
    get_input = raw_input

# System specific paths
RENDER_DEFAULT_DIRECTORY = OSX_RENDER_DIR
MB_DEFAULT_DIRECTORY = OSX_MB_DIR

# in terms of frames
SETTLE_TIME = 100
STARTFRAME = 0
# size of output image, must be a square for program to work
IMG_PIXELS = 500
# scales retract height, move height, move speed
global GLOBAL_SCALE
GLOBAL_SCALE = 1.0
# initial size of table in meters
TABLE_SIZE = 20.0
# final height to which pointer retracts after fold is finished, in meters
RETRACT_HEIGHT = 5.0
# height at which arm moves the shirt around, in meters
MOVE_HEIGHT = 3.0
# bounding box of shirt is scaled to a percentage of table size
SHIRT_SCALE = 0.8
# in terms of meters
MOVE_SPEED = 30.0/100.0
# max number of folds the robot can perform at once
NUM_ARMS = 2
# number of substeps within the fold
STEPS = 5
# Whether to use the model BAXTER gripper instead of the default generated pointer
BAXER_POINTER = False


# main function
def start():
    # Check if optional argument is used
    global num_cp
    num_cp = 0
    if (len(sys.argv) > 2):
        num_cp = get_cp()

    # Manual Input of Points
    # Enter XYZ points, converted to vertices
    print("Running folding simulation on file " + sys.argv[1])
    print("This simulation folds the input cloth from point A to point B, and saves the resulting file as an OBJ. You may specify multiple folds, by entering multiple pairs of points.")
    print("~~~")
    print("Enter points in the form of X,Y,Z coordinates (Ex: 1,2,3). Enter \"quit\" to begin the folding simulation with the given points")

    global fold_num
    fold_num = 0

    # take in points
    while(True):
        folds = get_input("Enter number of points to fold at once: ")
        if (folds.upper() == 'Q'):
            break
        else:
            folds = int(folds)
        if ((folds > NUM_ARMS) or (folds <= 0)):
            print("Number of folds attempted at once is greater than the number the robot can perform")
            break
        coords = []
        start_vertices = []
        end_vertices = []
        for n in range(folds):
            print("Enter two points:")
            p = get_input("  Enter point A: ")
            if (p[0].upper() == 'Q'):
                break
            else:
                temp = [int(x.strip()) for x in p.split(',')]
            p = get_input("  Enter point B: ")
            if (p[0].upper() == 'Q'):
                break
            else:
                start_vertices.append(temp)
                end_vertices.append([int(x.strip()) for x in p.split(',')])
        
        #timing
        start_time = time.clock()

        # Set up Scene
        if (fold_num == 0):
            setup_scene()
        else:
            setup_scene("folded/snapshots/shirt" + str(fold_num) + ".obj")

        start_vertices = [XYZ_to_vtx(x) for x in start_vertices]
        end_vertices = [XYZ_to_vtx(x) for x in end_vertices]

        # Fold the shirt
        global fold_num
        fold(fold_num+1, folds, start_vertices, end_vertices)
        om.MGlobal.viewFrame(mel.eval('playbackOptions -query -max'))
        #center_camera()
        render_frame(str(fold_num+1))
        fold_num += 1

        #timing
        print("The fold took " + str(time.clock() - start_time) + " seconds")

# setup functions
def setup_scene(name=sys.argv[1]):
    # imports shirt, scales to fit, converts to ncloth
    try:
        cmds.loadPlugin("objExport")
    except:
        pass
    mel.eval('file -f -options "mo=1" -ignoreVersion -typ "OBJ" -o "%s";' \
         % name)
    try:
        mel.eval('rename "Mesh" "shirt";')
    except:
        pass
    # scale shirt to fit
    create_table()
    if (fold_num == 0):
        bbx = cmds.xform("shirt", q=True, bb=True, ws=True)
        s_x_len = abs(bbx[3] - bbx[0])
        s_y_len = abs(bbx[4] - bbx[1])
        global GLOBAL_SCALE
        if (s_x_len >= s_y_len):
            GLOBAL_SCALE = s_x_len/(SHIRT_SCALE * TABLE_SIZE)
        else:
            GLOBAL_SCALE = s_y_len/(SHIRT_SCALE * TABLE_SIZE)
        cmds.select("shirt")
        cmds.move(0, 0.0001, 0, relative = True)
    cmds.scale(GLOBAL_SCALE, GLOBAL_SCALE, GLOBAL_SCALE, "table", centerPivot = True)
    shirt_to_nCloth()
    create_camera()
    #cmds.viewFit('camera1', all=True)
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
    mel.eval("makeCollideNCloth")
def create_camera():
    # creates a camera
    mel.eval('camera -centerOfInterest 5 -focalLength 35 -cameraScale 1;objectMoveCommand; cameraMakeNode 2 "";')
    cmds.select(clear=True)
    cmds.select("camera1")
    # render settings
    mel.eval('setAttr "frontShape.renderable" 0;')
    mel.eval('setAttr "topShape.renderable" 0;')
    mel.eval('setAttr "sideShape.renderable" 0;')
    mel.eval('setAttr "perspShape.renderable" 0;')
    mel.eval('setAttr "cameraShape1.renderable" 1;')
    # prep for render
    mel.eval('select -r camera1_aim; move -absolute -worldSpaceDistance 0 0 0;')
    mel.eval('select -r camera1; move -absolute -worldSpaceDistance 0 ' + str(5) + ' 0;')
    mel.eval('select -r shirt')
    cmds.viewFit('camera1', f=0.95*(SHIRT_SCALE/0.8))
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
def center_camera():
    # center the camera
    bbx = cmds.xform("shirt", q=True, bb=True, ws=True)
    centerX = (bbx[0] + bbx[3]) / 2.0
    centerZ = (bbx[2] + bbx[5]) / 2.0
    mel.eval('select -r camera1_aim; move -absolute -worldSpaceDistance ' + str(centerX) + ' 0 ' + str(centerZ) + ';')
    mel.eval('select -r camera1; move -absolute -worldSpaceDistance ' + str(centerX) + ' 5 ' + str(centerZ) + ';')
    cmds.viewFit('camera1', all=True)

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
def pixels_to_ws(x):
    return x * (TABLE_SIZE/IMG_PIXELS)
def get_position(vtx_string):
    # Gets the global position of a vertex
    # Input is a string of the form: "shirt.vtx[2]", or "table.vtx[36]"
    pos = mel.eval("xform -ws -q -t " + vtx_string + " ;")
    return pos
def cache(n, start, end):
    mel.eval('select -r shirt nCloth1;')
    mel.eval('doCreateNclothCache 5 { "0", "' + str(start) + '", "' + str(end) + '", "OneFile", "1", "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/","0","cache' + str(n) + '","0", "add", "1", "1", "1","1","1","mcx" } ;')
def render_frame(out):
    mel.eval('render -x ' + str(IMG_PIXELS) + ' -y ' + str(IMG_PIXELS) + ' camera1;')
    name = "shirt" + out
    os.system("sudo mv " + RENDER_DEFAULT_DIRECTORY + name + ".iff " + os.path.dirname(os.path.realpath(__file__)) + "/folded/images/" + name + ".iff")

# export functions
def export_mb(name):
    cmds.file(rename = name + ".mb")
    cmds.file(save = True, type = "mayaBinary")
    os.system("cp " + MB_DEFAULT_DIRECTORY + name + \
        ".mb " + os.path.dirname(os.path.realpath(__file__)) + "/folded/snapshots/" + name + ".mb")
def export_obj(name):
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/folded/snapshots/" + name + ".obj"
    print("Saving file as " + obj_path)
    cmds.select(clear=True)
    cmds.select("shirt")
    mel.eval('file -force -options "groups=0;ptgroups=1;materials=1;smoothing=1;normals=1" -typ "OBJexport" -pr -es "%s";' % obj_path)

# csv saving
def get_cp():
    num_points = 0
    with open(sys.argv[2], "rU") as f:
        os.path.dirname(os.path.realpath(__file__))
        reader = csv.reader(f)
        num_points = sum(1 for row in reader)

    return num_points
def save_cp(name, num_cp):
    #os.system("touch " + os.path.dirname(os.path.realpath(__file__)))
    with open(os.path.dirname(os.path.realpath(__file__)) + "/folded/snapshots/" + name + ".csv", "wb") as f:
        writer = csv.writer(f)
        for x in range(num_cp):
            vtx = get_position("shirt.vtx[" + str(x) + "]")
            writer.writerow(vtx)

# fold functions
def create_pointer(m):
    if (BAXER_POINTER == True):
        # import Baxter Pointer model and use it
        try:
            cmds.loadPlugin("objExport")
        except:
            pass
        name = os.path.dirname(os.path.realpath(__file__)) + "/models/baxter_gripper.obj"
        mel.eval('file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -rpr "gripper" -options "mo=1"  -pr "%s";' \
             % name)
        try:
            mel.eval('rename "gripper_Mesh" "pointer' + str(m) + '";')
        except:
            pass
    else:
        # Create a pointer mesh that represents the robot claw
        cmds.polyCone(name="pointer" + str(m), sx=3, r=0.5, h=2)
        cmds.select("pointer" + str(m))
        cmds.rotate("180deg", 0, 0, r=True)
        cmds.move(0, -1, 0, "pointer" + str(m) + ".scalePivot", "pointer" + str(m) + ".rotatePivot")
        cmds.move(0, 1, 0, absolute=True)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1)
    bbx = cmds.xform("table", q=True, bb=True, ws=True)
    cur_size = abs(bbx[3] - bbx[0])
    cmds.scale(cur_size/TABLE_SIZE, cur_size/TABLE_SIZE, cur_size/TABLE_SIZE, "pointer" + str(m), centerPivot = True)
    mel.eval('select -r pointer' + str(m) + '; sets -e -forceElement pointer_matSG;')
    mel.eval("makeCollideNCloth")
def bind_pointer(vtx, m):
    '''
    if (BAXER_POINTER == True):
        51905
    else:
    '''
    cmds.select(clear=True)
    mel.eval('select -r shirt.vtx[' + str(vtx) + '];')
    mel.eval('select -tgl pointer' + str(m) + '; createNConstraint transform 0;')
    mel.eval('select -r dynamicConstraint' + str(m) + ';')
    mel.eval('select -add pointer' + str(m) + '; Parent;')
    mel.eval('setAttr \"dynamicConstraintShape' + str(m) + '.glueStrength\" 0;')
    mel.eval('setKeyframe -t 0 { \"dynamicConstraintShape' + str(m) + '.gls\" };')
    mel.eval('setAttr \"dynamicConstraintShape' + str(m) + '.glueStrength\" 1;')
    mel.eval('setKeyframe -t 1 { \"dynamicConstraintShape' + str(m) + '.gls\" };')
def release_pointer(time, m):
    cmds.select(clear=True)
    mel.eval('select -tgl pointer' + str(m) + ';')
    mel.eval('setKeyframe -t ' + str(time) + ' { \"dynamicConstraintShape' + str(m) + '.gls\" };')
    mel.eval('setAttr \"dynamicConstraintShape' + str(m) + '.glueStrength\" 0;')
    mel.eval('setKeyframe -t ' + str(time+1) + ' { \"dynamicConstraintShape' + str(m) + '.gls\" };')
def move_pointer(x, y, z, m):
    cmds.select("pointer" + str(m))
    cmds.move(x, y, z, absolute=True, worldSpace=True, worldSpaceDistance=True)
def fold(n, m, A, B):
    # A, B are arrays containing the start and end points
    # n is the fold #
    # m is the number of grabbers
    # STARTFRAME is the frame at which the current fold starts
    # Set constants
    cmds.playbackOptions(min = STARTFRAME)

    # Movement
    for k in range(m):
        vtx1 = get_position("shirt.vtx[" + str(A[k]) + "]")
        vtx2 = get_position("shirt.vtx[" + str(B[k]) + "]")
        
        time1 = STARTFRAME
        time2 = int(MOVE_HEIGHT/MOVE_SPEED)
        time3 = int(math.hypot((vtx2[0]-vtx1[0]),(vtx2[2]-vtx1[2]))/MOVE_SPEED)
        time4 = int(MOVE_HEIGHT/MOVE_SPEED)
        
        ENDFRAME = time1 + time2 + time3 + time4 + SETTLE_TIME
        if ((m == 0) or (ENDFRAME > mel.eval('playbackOptions -query -max'))):
            cmds.playbackOptions(max = ENDFRAME)

        p_num = k+1

        create_pointer(p_num)
        move_pointer(vtx1[0], vtx1[1], vtx1[2], p_num)
        bind_pointer(A[k], p_num)
        cmds.select(clear=True)
        cmds.select("pointer" + str(p_num))
        cmds.setKeyframe(t=time1)
        move_pointer(vtx1[0], vtx1[1]+(MOVE_HEIGHT*GLOBAL_SCALE), vtx1[2], p_num)
        cmds.setKeyframe(t=time1+time2)
        move_pointer(vtx2[0], vtx1[1]+(MOVE_HEIGHT*GLOBAL_SCALE), vtx2[2], p_num)
        cmds.setKeyframe(t=time1+time2+time3)
        vtx2 = get_position("shirt.vtx[" + str(B[k]) + "]")
        move_pointer(vtx2[0], vtx2[1], vtx2[2], p_num)
        release_pointer(time1+time2+time3+time4, p_num)
        cmds.setKeyframe(t=time1+time2+time3+time4)
        move_pointer(vtx2[0], (RETRACT_HEIGHT*GLOBAL_SCALE), vtx2[2], p_num)
        cmds.setKeyframe(t=time1+time2+time3+time4+SETTLE_TIME)

    cache(n,STARTFRAME,ENDFRAME)
    if (STEPS > 1):
        for x in range(STEPS):
            om.MGlobal.viewFrame(x*(ENDFRAME-SETTLE_TIME)/STEPS)
            save_cp("shirt" + str(n) + "_" + str(x+1), num_cp)
            export_obj("shirt" + str(n) + "_" + str(x+1))

    om.MGlobal.viewFrame(ENDFRAME)
    save_cp("shirt" + str(n), num_cp)
    export_obj("shirt" + str(n))
    export_mb("shirt" + str(n))

# Main program
start()

# bake
'''
def bake(start, end):
    # Baking fold animation keyframes
    om.MGlobal.viewFrame(start)
    cmds.select("shirt")
    cmds.bakeResults(simulation=True, controlPoints=True, shape=True, time=(start, end))
'''

