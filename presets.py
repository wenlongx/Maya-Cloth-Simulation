import maya.standalone
maya.standalone.initialize()
import maya.mel as mel


# Every cloth must collide with itself
def collision():
    expr = ('setAttr "nClothShape1.collide" 1;'
        'setAttr "nClothShape1.selfCollide" 1;'
        'setAttr "nClothShape1.selfCollisionFlag" 4;'
        'setAttr "nClothShape1.collideStrength" 1;'
        'setAttr "nClothShape1.solverDisplay" 2;'
        'setAttr "nClothShape1.selfCollideWidthScale" 2;'
        'setAttr "nClothShape1.thss" .005;'
        'setAttr "nucleus1.gravity" 30;')
    mel.eval(expr)

def custom_shirt_cloth():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 4;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 40;'
        'setAttr "nClothShape1.compressionResistance" 40;'
        'setAttr "nClothShape1.bendResistance" 0.2;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.15;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 1.5;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.4;'
        'setAttr "nClothShape1.damp" 4;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)

# Burlap is rough, non-stretchy, moderately heavy and very damped. One may yet need to increase the stretch resistance further for high gravity or fast moving objects. If the material seems too springy try increasing the damp value.
def burlap():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 2;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 40;'
        'setAttr "nClothShape1.compressionResistance" 40;'
        'setAttr "nClothShape1.bendResistance" 3;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.603;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 1.5;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.4;'
        'setAttr "nClothShape1.damp" 4;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)

# Heavy Denim is moderately rough, very non-stretchy, moderately heavy and damped. One may yet need to increase the stretch resistance further for high gravity or fast moving objects. If the material seems too springy try increasing the damp value. 
def heavy_denim():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 0.8;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 50;'
        'setAttr "nClothShape1.compressionResistance" 20;'
        'setAttr "nClothShape1.bendResistance" 0.4;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.603;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 2;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.1;'
        'setAttr "nClothShape1.damp" 0.8;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)

# This simulates a soft loose knit sweater material. It is somewhat stretchy but lightweight and damped. One may yet need to increase the stretch resistance further for high gravity or fast moving objects. If the material seems too springy try increasing the damp value.
def loose_thick_knit():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 1;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 30;'
        'setAttr "nClothShape1.compressionResistance" 5;'
        'setAttr "nClothShape1.bendResistance" 0.5;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.603;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 0.8;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.4;'
        'setAttr "nClothShape1.damp" 1;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)

# Silk is smooth, lightweight, flexible but non-stretchy. Its low mass causes air drag and wind to affect it more. The compression resistance is relatively low, which helps lower resolution meshes maintain flexibility. For very high resolution meshes one may consider increasing the compression resistance. Depending on the scene one may need to increase the substeps and/or collision iterations to avoid stretching on colliding elements. Also one may yet need to increase the stretch resistance further for high gravity or fast moving objects. If the material seems to springy try also increasing the damp value.
def silk():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 0.5;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 60;'
        'setAttr "nClothShape1.compressionResistance" 10;'
        'setAttr "nClothShape1.bendResistance" 0.05;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.3;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 0.2;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.5;'
        'setAttr "nClothShape1.damp" 0.2;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)

# Thick leather is heavy, stiff and very damped. One may yet need to increase the stretch resistance further for high gravity or fast moving objects. If it is particularily stiff( like shoe leather ) the bend resistance may need to be increased as well. Deform resistance may also be useful.
def thick_leather():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 0.6;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 50;'
        'setAttr "nClothShape1.compressionResistance" 50;'
        'setAttr "nClothShape1.bendResistance" 10;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.727;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 3;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.2;'
        'setAttr "nClothShape1.damp" 8;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)

# A cotton t-shirt is medium weight and friction and is slightly stretchy with relatively damped motion. One may yet need to increase the stretch resistance further for high gravity or fast moving objects. If the material seems too springy try increasing the damp value.
def tshirt():
    collision()
    expr = ('setAttr "nClothShape1.bounce" 0;'
        'setAttr "nClothShape1.friction" 0.3;'
        'setAttr "nClothShape1.stickiness" 0;'
        'setAttr "nClothShape1.stretchResistance" 35;'
        'setAttr "nClothShape1.compressionResistance" 10;'
        'setAttr "nClothShape1.bendResistance" 0.1;'
        'setAttr "nClothShape1.bendAngleDropoff" 0.4;'
        'setAttr "nClothShape1.shearResistance" 0;'
        'setAttr "nClothShape1.pointMass" 0.6;'
        'setAttr "nClothShape1.lift" 0.05;'
        'setAttr "nClothShape1.drag" 0.05;'
        'setAttr "nClothShape1.tangentialDrag" 0.1;'
        'setAttr "nClothShape1.damp" 0.8;'
        'setAttr "nClothShape1.stretchDamp" 0.1;')
    mel.eval(expr)
