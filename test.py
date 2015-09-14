import os
import sys
os.environ["MAYA_LOCATION"] = "/usr/autodesk/maya"
os.environ["PYTHONHOME"] = "/usr/autodesk/maya"
os.environ["PATH"] = "/usr/autodesk/maya/bin:" + os.environ["PATH"]
os.environ["LD_LIBRARY_PATH"] = "/usr/autodesk/maya/lib:" + os.environ["LD_LIBRARY_PATH"]

sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\site-packages\setuptools-0.6c9-py2.6.egg")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\site-packages\pymel-1.0.0-py2.6.egg")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\site-packages\ipython-0.10.1-py2.6.egg")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\site-packages\ply-3.3-py2.6.egg") 
sys.path.append("C:\Program Files\Autodesk\Maya2011\\bin\python26.zip")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\DLLs")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\plat-win")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\lib-tk")
sys.path.append("C:\Program Files\Autodesk\Maya2011\\bin")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python")
sys.path.append("C:\Program Files\Autodesk\Maya2011\Python\lib\site-packages")


import maya.standalone
maya.standalone.initialize(name='python')
