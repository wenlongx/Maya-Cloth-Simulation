import sys
#sys.path.insert(0, "/Applications/Autodesk/maya2015/Maya.app/Contents/Frameworks/Python.framework/Versions/Current/lib/python2.7/site-packages")
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
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
HEIGHT = 2
MOVE_SPEED = (30/100.0)
SETTLE_TIME = 50
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
    global next_frame
    next_frame = 1
    global cache_created
    cache_created = False

    # Set up scene
    import_shirt()
    create_table()
    create_camera()

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
            coords.append(temp)
            coords.append([int(x.strip()) for x in p.split(',')])
        for c in coords:
            vertices.append(XYZ_to_vtx(c))
        # Fold the shirt
        global fold_num
        global next_frame
        next_frame = fold(vertices[0], vertices[1], fold_num+1, next_frame)
        fold_num += 1
    #mel.eval('doCreateNclothCache 5 { "0", "0", "' + str(next_frame) + '", "OneFile", "1", "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/","0","cache","0", "merge", "1", "1", "1","1","1","mcx" } ;')
    #bake(next_frame)
    export_mb(OUT_NAME)

# setup functions
# TODO - all checked off
def import_shirt():
    # imports shirt, scales to fit, converts to ncloth
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
    cmds.currentTime(start)
    cmds.select("shirt")
    cmds.bakeResults(simulation=True, controlPoints=True, shape=True, time=(start, end))
def render_frame(name):
    mel.eval('render -x 500 -y 500 camera1;')
    os.system("sudo mv /private/var/root/Documents/maya/projects/default/images/" + sys.argv[1] + ".iff " + os.path.dirname(os.path.realpath(__file__)) + "/folded/images/" + name + ".iff")


# export functions
def export_mb(name):
    cmds.file(rename = name + ".mb")
    cmds.file(save = True, type = "mayaBinary")
    os.system("cp /private/var/root/Documents/maya/projects/default/" + name + \
        ".mb " + os.path.dirname(os.path.realpath(__file__)) + "/folded/" + name + ".mb")
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

# fold functions
def create_pointer(n):
    # Create a pointer mesh that represents the robot claw
    cmds.polyCone(name="pointer"+str(n), sx=3, r=0.5, h=2)
    cmds.select(clear=True)
    cmds.select("pointer"+str(n))
    mel.eval('select -r pointer' + str(n) + ' ; sets -e -forceElement pointer_matSG;')
    cmds.select("pointer"+str(n))
    cmds.rotate("180deg", 0, 0, r=True)
    cmds.move(0, -1, 0, "pointer" + str(n) + ".scalePivot", "pointer" + str(n) + ".rotatePivot")
    cmds.move(0, 1, 0, absolute=True)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1)
    mel.eval("makeCollideNCloth")
def bind_pointer(vtx, n, time):
    cmds.select(clear=True)
    mel.eval('select -r shirt.vtx[' + str(vtx) + '];')
    mel.eval('select -tgl pointer' + str(n) + '; createNConstraint transform 0;')
    mel.eval('select -r dynamicConstraint' + str(n) + ';')
    mel.eval('select -add pointer' + str(n) + '; Parent;')
    #mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 0;')
    #mel.eval('setKeyframe { \"dynamicConstraintShape' + str(n) + '.gls\" };')
    #temp = cmds.currentTime(query=True)
    #cmds.currentTime(temp+1)
    mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 0;')
    mel.eval('setKeyframe -t 0 { \"dynamicConstraintShape' + str(n) + '.gls\" };')
    mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 1;')
    mel.eval('setKeyframe -t ' + str(time) + ' { \"dynamicConstraintShape' + str(n) + '.gls\" };')
def release_pointer(n, time):
    cmds.select(clear=True)
    mel.eval('select -tgl pointer' + str(n))
    mel.eval('setKeyframe -t ' + str(time) + ' { \"dynamicConstraintShape' + str(n) + '.gls\" };')
    mel.eval('setAttr \"dynamicConstraintShape' + str(n) + '.glueStrength\" 0;')
    mel.eval('setKeyframe -t ' + str(time+1) + ' { \"dynamicConstraintShape' + str(n) + '.gls\" };')
def move_pointer(x, y, z, n):
    cmds.select("pointer" + str(n))
    cmds.move(x, y, z, absolute=True, worldSpace=True, worldSpaceDistance=True)
def fold(A, B, n, STARTFRAME = 0):
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
    cmds.playbackOptions(min = 0)
    cmds.playbackOptions(max = ENDFRAME)

    # Movement

    create_pointer(fold_num+1)
    move_pointer(vtx1[0], vtx1[1], vtx1[2], n)
    bind_pointer(A, n, time1)
    cmds.select(clear=True)
    cmds.select("pointer" + str(n))
    cmds.setKeyframe(t=time1)
    #cmds.currentTime(time1 + time2)
    move_pointer(vtx1[0], vtx1[1]+HEIGHT, vtx1[2], n)
    cmds.setKeyframe(t=time1+time2)
    #cmds.currentTime(time1 + time2 + time3)
    move_pointer(vtx2[0], vtx1[1]+HEIGHT, vtx2[2], n)
    cmds.setKeyframe(t=time1+time2+time3)
    vtx2 = get_position("shirt.vtx[" + str(B) + "]")
    #cmds.currentTime(time1 + time2 + time3 + time4)
    move_pointer(vtx2[0], vtx2[1], vtx2[2], n)
    release_pointer(n, time1+time2+time3+time4)
    cmds.setKeyframe(t=time1+time2+time3+time4)
    #cmds.currentTime(time1 + time2 + time3 + time4 + SETTLE_TIME)
    move_pointer(vtx2[0], RETRACT_HEIGHT, vtx2[2], n)
    cmds.setKeyframe(t=time1+time2+time3+time4+SETTLE_TIME)

    global cache_created
    if (cache_created):
        # check out why this line does what it does
        # mel.eval('performCreateNclothCache 1 add')
        #http://files.crescentinc.co.jp/Autodesk_Maya_2015_dlm/Autodesk_Maya_2015_dlm/x64/Maya/Autodesk/Maya2015/scripts/others/performCreateNclothCache.mel
        # ^ see whats going on with the options and others
        
        if (n == 2):
            pass
            #mel.eval('createNode "cacheBlend" -n "cacheBlend1" -p "nClothShape1";')
            #mel.eval('select -r nClothShape1; string $cacheBlend15[] = `cacheFileCombine`;')
            #mel.eval('aliasAttr cacheCache1 cacheBlend1.cacheData[0].weight ;')
        #mel.eval('aliasAttr cacheCache' + str(n) + ' cacheBlend1.cacheData[' + str(n-1) + '].weight ;')


        
        mel.eval('select -r shirt nCloth1;')
        mel.eval('optionVar -intValue nclothRefresh 1; \
            optionVar -intValue nclothCacheDistrib 1; \
            optionVar -intValue nclothCacheTimeRange 0; \
            optionVar -floatValue nclothCacheStartTime ' + str(STARTFRAME) + '; \
            optionVar -floatValue nclothCacheEndTime ' + str(ENDFRAME) + '; \
            optionVar -stringValue nclothCacheFormat "mcx"; \
            optionVar -sv nclothCacheDirName "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/"; \
            optionVar -stringValue nclothCacheName "cache' + str(n) + '"; \
            optionVar -intValue nclothCachePerGeometry 1; \
            optionVar -intValue nclothCacheAsFloats 1; \
            optionVar -floatValue nclothCacheSimulationRate 1; \
            optionVar -intValue nclothCacheMergeDelete 1; \
            optionVar -intValue nclothCacheSampleMultiplier 1; \
            optionVar -intValue nclothCacheInheritModifications 1; \
            optionVar -intValue nclothCacheUsePrefix 0;')
        '''
        mel.eval('performCreateNclothCache 0 "add";')
        '''
        #mel.eval('setCacheEnable 1 0 {};')
        #om.MGlobal.viewFrame(1)
        #mel.eval('setCacheEnable 0 0 {};')
        #render_frame(str(n))
        mel.eval('select -r shirt nCloth1;')
        mel.eval('doCreateNclothCache 5 { "0", "' + str(STARTFRAME-1) + '", "' + str(ENDFRAME) + '", "OneFile", "1", "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/","0","cache' + str(n) + '","0", "add", "1", "1", "1","1","1","mcx" } ;')
        om.MGlobal.viewFrame(ENDFRAME)
    else:
        mel.eval('select -r shirt nCloth1;')
        mel.eval('doCreateNclothCache 5 { "0", "' + str(STARTFRAME) + '", "' + str(ENDFRAME) + '", "OneFile", "1", "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/","0","cache' + str(n) + '","0", "add", "1", "1", "1","1","1","mcx" } ;')
        cache_created = True
        om.MGlobal.viewFrame(ENDFRAME)
        mel.eval('deleteCacheFile 3 { "keep", "cache' + str(n) + 'Cache1", "nCloth" } ;')
    #om.MGlobal.viewFrame(ENDFRAME-1)
    render_frame(str(n))

    return ENDFRAME
# C contains tuples of XYZ points
    # C = [ [0,0,0]
    #       [2,2,2]
    #       [2,1,2]
    #       [1,0,0] ]
    # in this case, [0,0,0] would fold to [2,2,2] and [2,1,2] folds to [1,0,0]



start()
'''

deleteCacheFile 3 { "keep", "cache1Cache1", "nCloth" } ;


attachGeometryCache;
doImportCacheArgList(0,{});
np_getPrimaryProjectFileRules 0;

aliasAttr  cache1Cache1 cacheBlend1.cacheData[0].weight ;
// 1 // 
aliasAttr  cache2Cache1 cacheBlend1.cacheData[1].weight ;

aliasAttr  cache3Cache1 cacheBlend1.cacheData[2].weight ;

proc setOptionVars(int $forceFactorySettings)
{
    global string $gCacheCurrentProject;
    global string $gNclothCacheAutomaticName;
    global string $gNclothCacheSceneNameForPrefs;   

    string $currSceneName = `file -q -loc`;
    if ($currSceneName != $gNclothCacheSceneNameForPrefs) {
        // We only want the cache name and directory name prefs to exist
        // for the time that the scene is opened. We don't want them
        // to be saved for the next session or next scene.
        //
        optionVar -rm nclothCacheDirName; optionVar -rm nclothCacheName;
    }
    optionVar -intValue nclothRefresh 1;
    optionVar -intValue nclothCacheDistrib 1;
    optionVar -intValue nclothCacheTimeRange 0;
    optionVar -floatValue nclothCacheStartTime sssssssssssaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa----------------;
    optionVar -floatValue nclothCacheEndTime aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa----------------;
    optionVar -stringValue nclothCacheFormat "mcx";
    optionVar -sv nclothCacheDirName "----------------------------------------------------------------------------------------------------";
    optionVar -stringValue nclothCacheName "cache------------------------------------------------------------------------------------------";
    optionVar -intValue nclothCachePerGeometry 1;
    optionVar -intValue nclothCacheAsFloats 1;
    optionVar -floatValue nclothCacheSimulationRate 1;
    optionVar -intValue nclothCacheMergeDelete 0;
    optionVar -intValue nclothCacheSampleMultiplier 1;
    optionVar -intValue nclothCacheInheritModifications 0;
    optionVar -intValue nclothCacheUsePrefix 0;
}













use add instead of merge or replace

    global cache_created
    if (cache_created):
        cmds.select( 'nClothShape1', r=True )
        newBlend = cmds.cacheFileCombine()
        print(newBlend)

cacheFile -refresh -appendFrame  -cnd nClothShape1 -startTime 90 -endTime 180 -simulationRate 1 -sampleMultiplier 1 -noBackup;

        cmds.cacheFileCombine( newBlend[0], e=True, cc='cacheFile2' )
        om.MGlobal.viewFrame(20)
        render_frame(str(n))
        #mel.eval('cacheFile -attachFile -fileName "cache" -directory "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/"  -cnm "nClothShape1" -ia nClothShape1.positions;')
        #mel.eval('doAppendNclothCache 6 ' + str(STARTFRAME) + ' ' + str(ENDFRAME) +' 1 1')
        #mel.eval('cacheFile -refresh -appendFrame -cnd nClothShape1 -startTime ' + str(STARTFRAME) + ' -endTime ' + str(ENDFRAME) + ' -simulationRate 1 -rf 20 -sampleMultiplier 1 -directory "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/" -noBackup;')
        #  -directory "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/"
    else:
        mel.eval('select -r shirt nCloth1;')
        mel.eval('doCreateNclothCache 5 { "0", "' + str(STARTFRAME) + '", "' + str(ENDFRAME) + '", "OneFilePerFrame", "1", "' + os.path.dirname(os.path.realpath(__file__)) + '/folded/cache/","0","cache","0", "add", "0", "1", "1","1","1","mcx" } ;')
        cache_created = True


select -r shirt nCloth1;
doCreateNclothCache 1 { "0", "1", "90", "OneFile", "1", "~/Desktop/","0","cache1","1", "add", "0", "1", "1","1","1","mcx" } ;
select -r shirt nCloth1;
doAppendNclothCache 6 90 180 1 1;


select -r nCloth1 ;
nClothCacheOpt;

performCreateNclothCache 1 "add";

performCreateNclothCache 0 add;
doCreateNclothCache 5 { "3", "1", "90", "OneFile", "1", "","0","n1","1", "add", "0", "1", "1","0","1","mcx" } ;

cacheFile -attachFile -fileName "n1_nClothShape1" -directory "/Users/wenlongx/Documents/maya/projects/default/cache/nCache/folded"  -cnm "nClothShape1" -ia nClothShape1.positions;

// n1_nClothShape1Cache1 // 
// /Users/wenlongx/Documents/maya/projects/default/cache/nCache/folded/n1_nClothShape1.xml // 
// doCreateNclothCache 5 { "3", "1", "90", "OneFile", "1", "","0","n1","1", "add", "0", "1", "1","0","1","mcx" }  // 

select -r nCloth1 ;

nClothAppendOpt;
performAppendNclothCache 1;

doAppendNclothCache 6 91 180 1 1;
cacheFile -refresh -appendFrame  -cnd nClothShape1 -startTime 91 -endTime 180 -simulationRate 1 -sampleMultiplier 1 -noBackup;
refreshAE;
listHistory -pdo true -lf false -il 2 "|nCloth1";
listHistory -pdo true -lf false -il 2 -f true "|nCloth1";
floatField -edit -value `currentTime -query` MayaWindow|toolBar6|MainTimeSliderLayout|formLayout9|floatField1;
// MayaWindow|toolBar6|MainTimeSliderLayout|formLayout9|floatField1 // 
if (`window -exists OptionBoxWindow`) deleteUI -window OptionBoxWindow;
saveOptionBoxSize();

'''

'''
select -r nCloth1 ;
doCreateNclothCache 5 { "3", "1", "90", "OneFile", "1", "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache","0","","0", "add", "0", "1", "1","0","1","mcx" } ;
cacheFile -attachFile -fileName "nClothShape1" -directory "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/"  -cnm "nClothShape1" -ia nClothShape1.positions;
// nClothShape1Cache1 // 
// /Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/nClothShape1.xml // 
select -r nCloth1 ;
doCreateNclothCache 5 { "3", "91", "180", "OneFile", "1", "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache","0","nClothShape2","1", "add", "0", "1", "1","0","1","mcx" } ;
cacheFile -attachFile -fileName "nClothShape2_nClothShape1" -directory "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/"  -cnm "nClothShape1" -ia nClothShape1.positions;
// nClothShape2_nClothShape1Cache1 // 
// /Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/nClothShape2_nClothShape1.xml // 



doCreateGeometryCache 6 { "3", "1", "88", "OneFile", "1", "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache","0","c","0", "add", "0", "1", "1","0","1","mcx","0" } ;
cacheFile -attachFile -fileName "c" -directory "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/"  -cacheFormat "mcx"  -ia cacheSwitch1.inp[0];
// cCache1 // 
// /Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/c.xml // 
cacheFile -refresh -appendFrame  -points outputCloth1 -startTime 88 -endTime 178 -simulationRate 1 -sampleMultiplier 1 -noBackup;


doCreateNclothCache 5 { "3", "1", "88", "OneFilePerFrame", "1", "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache","0","test","1", "add", "0", "1", "1","0","1","mcx" } ;
cacheFile -attachFile -fileName "test_nClothShape1" -directory "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/"  -cnm "nClothShape1" -ia nClothShape1.positions;
// Result: test_nClothShape1Cache1 // 
// Result: /Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/test_nClothShape1.xml // 
playbackOptions -min 0 -max 178 ;
// Warning: Nucleus evaluation skipped, frame change too large // 
currentTime 178 ;
select -r shirt nCloth1 table ;
select -tgl table ;
doAppendNclothCache 6 89 178 1 1;
cacheFile -refresh -appendFrame  -cnd nClothShape1 -startTime 89 -endTime 178 -simulationRate 1 -sampleMultiplier 1 -noBackup;


select -r shirt ;
doCreateNclothCache 5 { "3", "0", "260", "OneFile", "1", "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache","0","cache_test3","0", "add", "0", "1", "1","0","1","mcx" } ;
cacheFile -attachFile -fileName "cache_test3" -directory "/Users/wenlongx/Desktop/vision_lab/Maya-Cloth-Simulation/folded/cache/"  -cnm "nClothShape1" -ia nClothShape1.positions;
'''

