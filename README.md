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
This python program simulates folding a cloth multiple times, and dynamically generates the resulting models and images after each fold performed on the cloth. To simulate holding the model being folded, run one of the following:

    $ path/to/mayapy main.py path/to/shirt_model.obj  
    $ path/to/mayapy main.py path/to/shirt_model.obj points.csv

The program accepts 1 or 2 command line arguments, and a description of the output files is included at the top of **main.py**. All outputs will be generated in the **/folded/** directory. This will generate a command line prompt, which will explain the rest of the folding process. The optional parameter is a CSV file, which specifies whether to record the progress of the boundary points (ones used to generate the shirt model) as an output CSV file as well. The optional CSV file must be the same one used to generate the shirt_model.obj (first parameter), or a wrong number of boundary points will be recorded. Below are some constants that define how the folding occurs:

### Some Constants
**SETTLE_TIME** - Time for the cloth to settle to its final position after a fold. Specified in "frames" (conversion is 30 frames to 1 second). Default is 100 frames.  
**TABLE_SIZE** - Size of the table that holds the shirt model. Specified in arbitrary units. Will be scaled to a size such that the bounding box of the shirt is X% of the table, where X is specified by SHIRT_SCALE.  
**RETRACT_HEIGHT** - Height to which the gripper will retract to after the fold is finished. Specified in the same arbitrary units as TABLE_SIZE and MOVE_HEIGHT.  
**MOVE_HEIGHT** - Height at which gripper will perform the fold. Speficied in the same arbitrary units as TABLE_SIZE and RETRACT_HEIGHT  
**SHIRT_SCALE** - Percentage that the table is scaled to. See TABLE_SIZE. Default is 80%.  
**GLOBAL_SCALE** - Scales the RETRACT_HEIGHT, MOVE_HEIGHT accordingly   
**MOVE_SPEED** = Speed at which pointer will move. Specified in terms of ul/frame, where ul is the arbitrary unit used in TABLE_SIZE, RETRACT_HEIGHT, and MOVE_HEIGHT  
**IMG_PIXELS** - Output image is a square .iff file of this size  
**STEPS** - You can specify if you want to take snapshots (obj models and csv points) of the shirt model during the fold. STEPS defaults to 0, but setting it to a value greater than 1 results in stopping the fold X times to take snapshots of the model. Times are subdivided equally  
**NUM_ARMS** - Maximum number of grippers the robot has. Default value is 2 arms.
**BAXTER_POINTER** - Simulates the folding using a realistic model of the Baxter Research Robot's hand with standard narrow fingers  



**This section is not yet finished, still under construction**  
**Features to come:**
* use sockets to give commands
* the folder **/in_progress/** is used to hold pieces of code I may or may not come back to
