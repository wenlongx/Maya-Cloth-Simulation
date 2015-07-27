# Don't understand this
# http://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2015/ENU/Maya/files/Python-Python-from-an-external-interpreter-htm.html

# Takes 1 command line arguments
#   1) string; path to CSV point file

# Generates in your current directory
#   1) an OBJ file called out.obj
#   2) a Maya Binary file called out.mb

import sys
#sys.path.insert(0, "/Applications/Autodesk/maya2015/Maya.app/Contents/Frameworks/Python.framework/Versions/Current/lib/python2.7/site-packages")
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
import maya.mel as mel
import csv
import os

SUBDIVISIONS = 3
OUT_NAME = "shirt"

# Read from CSV file, store in points
def read_csv():
    """Opens CSV file and stores each points (tuple) in a list"""
    points = []
    with open(sys.argv[1], "rU") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 3:
                print("Points in CSV file are greater than 3 dimensions")
                sys.exit(0)
            # If set of points is 2 dimensional, autogenerate the 3rd dimension
            elif len(row) == 2:
                row.append(['0'])
            points.append(tuple(map(float, row)))
    return points

# Create polygon called shirt based on points
def generate(pts):
    """Takes in a list of tuples (set of 3D points) and generates a polygon model"""
    cmds.polyCreateFacet(name="shirt", p=points)
    cmds.polyTriangulate()
    cmds.polySubdivideFacet(dv=SUBDIVISIONS)
    cmds.polyTriangulate()

# Exports file as a Maya Binary
def export_mb(name):
    cmds.file(rename = name + ".mb")
    cmds.file(save = True, type = "mayaBinary")
    os.system("cp /private/var/root/Documents/maya/projects/default/scenes/" + name + ".mb " + os.path.dirname(os.path.realpath(__file__)) + "/" + name + ".mb")

# Exports file as an OBJ
def export_obj(name):
    cmds.loadPlugin('objExport')
    obj_path = os.path.dirname(os.path.realpath(__file__)) + "/" + name + ".obj"
    mel.eval('file -force -options "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1" -type "OBJexport" -pr -ea "%s";' % obj_path)

# Main Program
points = read_csv()
generate(points)
export_obj(OUT_NAME)
