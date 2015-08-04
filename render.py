# Takes 2 command line arguments
#   1) string; path to OBJ shirt model
#   2) string; whether to render a flat image or to render using ambient occlusion
#       ao - represents Ambient Occlusion    flat - represents flat image

# Generates an OBJ file in the folded/ directory
#   1) an OBJ file called folded_vtx1_vtx2.obj, where vtx1 is the moved vertex and vtx2 is the target vertex

# Ambient Occlusion reference
# https://github.com/swirch/rl/blob/master/ao.py

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import time
import sys
import os

import ao

CAMERA_HEIGHT = 20.0
RENDER_WIDTH = 400
RENDER_HEIGHT = 400

# Import shirt, convert to nCloth
def import_shirt():
    cmds.loadPlugin("objExport")
    mel.eval('file -f -options "mo=1" -ignoreVersion -typ "OBJ" -o "%s";' \
         % sys.argv[1])

# Convert to OBJ
def export_obj(name):
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/out/" + name
    for x in VERTICES:
        obj_path += "_" + str(x)
    obj_path += ".obj"
    print("Saving file as " + obj_path)
    cmds.select(clear=True)
    cmds.select("shirt")
    mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;' +  \
        'smoothing=1;normals=1" -typ "OBJexport" -pr -es "%s";' % obj_path)

# Renders a bird's-eye of the final result
def render():
    # create camera
    cam = mel.eval('camera -centerOfInterest 5 -focalLength 35 -cameraScale 1;')
    mel.eval('objectMoveCommand; cameraMakeNode 2 "";')
    #mel.eval('rename |camera1_group|camera1 "cam" ;')
    #mel.eval('rename |camera1_group|camera1_aim "cam_aim" ;')
    cmds.select(clear=True)
    cmds.select("camera1")
    cmds.move(0, CAMERA_HEIGHT, 0, absolute=True, worldSpace=True, worldSpaceDistance=True)
    cmds.select("camera1_aim")
    cmds.move(0, 0, 0, absolute=True, worldSpace=True, worldSpaceDistance=True)

    # render settings
    mel.eval('setAttr "frontShape.renderable" 0;')
    mel.eval('setAttr "topShape.renderable" 0;')
    mel.eval('setAttr "sideShape.renderable" 0;')
    mel.eval('setAttr "perspShape.renderable" 0;')
    mel.eval('setAttr "cameraShape1.renderable" 1;')

    # render respective image
    if ( (not(len(sys.argv) < 3)) and (sys.argv[2].lower() == "ao")):
        ao_render(cam)
    else:
        flat_render(cam)


def ao_render(c):
    # load the respective plugins
    ao.setup_ao("polySurface1")
    # render from command line
    cmds.Mayatomr(render=True, logFile=True, layer='ao', xResolution=RENDER_WIDTH, yResolution=RENDER_HEIGHT, camera=c[0])
    #cmds.render(c[0])

def flat_render(c):
    mel.eval('select -r shirt;')
    mel.eval('shadingNode -asShader lambert;')
    mel.eval('rename lambert2 "shirt_mat";')
    mel.eval('sets -renderable true -noSurfaceShader true' + \
        '-empty -name -shirt_matSG;')
    mel.eval('connectAttr -f shirt_mat.outColor shirt_matSG.surfaceShader;')
    mel.eval('setAttr "shirt_mat.color" -type double3 1 1 1;')
    mel.eval('setAttr "shirt_mat.ambientColor" -type double3 1 1 1;')
    mel.eval('select -r shirt ; sets -e -forceElement shirt_matSG;')

    cmds.render(c[0], x=RENDER_WIDTH, y=RENDER_HEIGHT)

# Main program
ao.loadMentalRayPlugin()
start = time.time()
print("Rendering file " + sys.argv[1] + " with Mental Ray")
import_shirt()
render()
end = time.time()
print("Rendering took " + str(end-start) + " seconds to run")

cmds.file(rename = "something.mb")
cmds.file(save=True, type="mayaBinary")
os.system("cp /private/var/root/Documents/maya/projects/default/something.mb ~/Desktop/something.mb")
