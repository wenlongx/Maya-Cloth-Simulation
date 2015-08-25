# Ambient Occlusion reference
# https://github.com/swirch/rl/blob/master/ao.py

import sys
sys.path.insert(0, "/Applications/Autodesk/mentalRayForMaya2015/scripts/")
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import mentalray

def loadMentalRayPlugin():
    name = 'Mayatomr'
    if not cmds.pluginInfo(name, q=True, loaded=True):
        cmds.loadPlugin(name)
        cmds.pluginInfo(name, edit=True, autoload=True)
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mentalRay', type='string')
    print ('# Result: mental ray Plugin loaded #')

# set up scene for ambient occlusion
def setup_ao(target):
    # setup backdrop
    cmds.polyPlane(name="ao_backdrop", w=15, h=15)
    cmds.select(clear=True)
    cmds.select("ao_backdrop")
    cmds.move(0, -0.5, 0, relative=True)
    '''
    mel.eval('select -r ao_backdrop;')
    mel.eval('sets -renderable true -noSurfaceShader true ' + \
        '-empty -name -table_matSG;')
    mel.eval('select -r ao_backdrop ; sets -e -forceElement table_matSG;')
    '''

    # create new render layer
    select_objs(target)
    cmds.createRenderLayer(name='ao', makeCurrent=True)

    # create a new surface shader for the ambient occlusion shader
    surf_shader = cmds.shadingNode('surfaceShader', asShader=True, \
        name='amb_occl_surf_shader')
    ao_shader = cmds.shadingNode('mib_amb_occlusion', asShader=True, name='amb_occl')
    cmds.connectAttr(ao_shader + '.outValue', surf_shader + '.outColor')

    # create a new shading group for the ao shader
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='aoSG')
    cmds.connectAttr(surf_shader + '.outColor', sg + '.surfaceShader')

    # switch to the ao render layer
    cmds.editRenderLayerGlobals(currentRenderLayer='ao')
    #mel.eval('editRenderLayerGlobals -currentRenderLayer defaultRenderLayer;')

    select_objs(target)
    objects = cmds.ls(selection=True)
    cmds.select(objects)
    mel.eval('sets -e -forceElement ' + sg)
    change_ao_settings()
    change_render_settings()

# selects the objects in ao layer
def select_objs(target_obj):
    """selects backdrop as well as target cloth"""
    cmds.select(clear=True)
    cmds.select(target_obj)
    cmds.select("ao_backdrop", add=True)

# change ao settings to values; defaults are specified
def change_ao_settings(num_samples=128, spread=0.8, max_distance=0):
    """changes settings of mib_amb_occlusion"""
    cmds.setAttr('amb_occl.samples', num_samples)
    cmds.setAttr('amb_occl.spread', spread)
    cmds.setAttr('amb_occl.max_distance', max_distance)


# changes default render settings to get a decent render
def change_render_settings():
    """changes mental ray render settings to appropriate defaults"""
    # switch to mental ray rendering
    cmds.setAttr('defaultRenderGlobals.ren', 'mentalRay', type='string')
    # create the mental ray rendering nodes so they can be changed
    mel.eval('miCreateDefaultNodes')
    # set filter to gaussian as layer overide
    cmds.editRenderLayerAdjustment( 'miDefaultOptions.filter', layer='ao' )
    cmds.setAttr('miDefaultOptions.filter', 2);
    # set the max/min samples
    cmds.setAttr('miDefaultOptions.maxSamples', 2)
    cmds.setAttr('miDefaultOptions.minSamples', 0)
    
    mel.eval('setAttr "miDefaultOptions.rayTracing" 0;')
    mel.eval('setAttr "defaultRenderGlobals.imageFormat" 3;')
    mel.eval('setAttr "miDefaultFramebuffer.datatype" 16;')
    mel.eval('setAttr "defaultResolution.width" 640;')
    mel.eval('setAttr "defaultResolution.height" 480;')
    mel.eval('setAttr "defaultResolution.pixelAspect" 1;')

loadMentalRayPlugin()
