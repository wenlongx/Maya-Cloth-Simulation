# Maya-Cloth-Simulation  
A collection of programs that use Autodesk Maya's nucleus engine to simulate actions performed on cloth (more specifically, a shirt). The programs can:
* generate a cloth model from a CSV file
* simulate a cloth model being held from several points
* simulate a cloth model being folded multiple times
* generate bird's-eye view images of the cloth model after each fold  
  
---
# Scripts and Expected Output
- **/generate\_shirt.py** should create a **.obj** file in the **/models/** directory.
- **/drop\_shirt.py** should create an **.obj** file and a **.mb** file in the **/dropped/** directory.  
- **/main.py** should create an **.obj** file and a **.mb** file in the **/folded/snapshots/** directory, as well as an **.iff** image in the **/folded/images/** directory, for each fold that it performs.

# Setup
Make sure Autodesk Maya 2015 is installed on your computer; download links for Student/Education can be found [here](http://www.autodesk.com/education/free-software/maya). Make sure Python is installed as well; it can be found [here](https://www.python.org).  

# Usage
## Locate mayapy
The following programs use a Python interpreter called **mayapy** provided by the Autodesk Maya installation. You must use this interpreter (and not your default Python installation). You can find **mayapy** executable in the /bin directory of Maya. For Mac users, it should be located in /Maya.app/Contents/bin.  

## Generating shirt model from CSV file
Your CSV file should contain 3-Dimensional points in the form X, Y, Z. By default, gravity in the physics simulation is in the -Y direction, so keep this in mind when generating your CSV file. A demo CSV file is stored in the /models/ folder by default.  
To generate a shirt model, run the script generate\_shirt.py:  

    $ path/to/mayapy generate_shirt.py path/to/file.csv  

The resulting generated OBJ file is called **shirt.py**, and is stored in:
    
    $ path/to/current/dir/models/shirt.py


## Simulating model being held from multiple points
To simulate holding the shirt model from a point(s), run the following, where *points* are integers:  

    $ path/to/mayapy drop_shirt.py point1 point2 ... pointn  

The python program accepts 1 or more points, and if there is more than 1 point, will simulate the cloth falling as if all the points were pinned into place. This python program generates both a Maya Binary file called **dropped_point1_...pointn.mb** and an OBJ file called **dropped_point1_...pointn.obj** in the **/dropped/** directory.

## Simulating model being folded multiple times
This python program simulates folding a cloth multiple times, and dynamically generates the resulting models and images after each fold performed on the cloth. To simulate holding the model being folded, run the following:

    $ path/to/mayapy main.py path/to/shirt_model.obj  

This will generate a command line prompt, which explains the rest.  

**This section is not yet finished, still under construction**  
**Features to come:**
* multiple folds at once
* GUI

