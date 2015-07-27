# Maya-Cloth-Simulation
Generates a shirt model from a CSV file, and simulates it being held from random points  
---
# Setup
Make sure Autodesk Maya 2015 is installed on your computer; download links for Student/Education can be found [here](http://www.autodesk.com/education/free-software/maya). Make sure Python is installed as well; it can be found [here](https://www.python.org).  

# Usage
## Locate mayapy
The following programs use a Python interpreter called **mayapy** provided by the Autodesk Maya installation. You must use this interpreter (and not your default Python installation). You can find **mayapy** executable in the /bin directory of Maya. For Mac users, it should be located in /Maya.app/Contents/bin.  

## Generating Shirt Model from CSV file
Your CSV file should contain 3-Dimensional points in the form X, Y, Z. By default, gravity in the physics simulation is in the -Y direction, so keep this in mind when generating your CSV file.  
To generate a shirt model, run the script generate\_shirt.py:  
        $ path/to/mayapy generate_shirt.py path/to/file.csv  

## Simulating Model being held from multiple points
To simulate holding the shirt model from a point(s), run the following:  
        $ path/to/mayapy drop_shirt.py point_1 point_2 ... point_n  
The python program accepts 1 or more points, and if there is more than 1 point, will simulate the cloth falling as if all the points were pinned into place.

## Expected Output
**generate\_shirt.py** should create a **.obj** file in the directory the script is located.  
**drop\_shirt.py** should create a **.obj** file in the **/out/** directory.  
