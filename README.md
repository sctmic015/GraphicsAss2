# Author: SCTMIC015

## Set Up information:

I could not run the program (even when the initial skeleton was given to us)
within a virtual environment on linux. I assume it has something to do with my 
linux distribution. However, The program ran perfectly  on a linux system provided the packages within the 
"requirements.txt" file were installed outside of a virtual environment. However, the program worked fine within a virtual
environment in windows. 

Setup within a virtual environment on windows is as follows.
Assuming that python3 and python3-venv installed.

All instructions are exectuted from within the SCTMIC015Ass1 directory:

1) To build the virtual environment and install necessary packages using a python script:

```
> python3 MakeWindows.py
```



2) To activate the virtual environment:

```
> ./venv/Scripts/activate


```

3) To run the skeleton code:

- To load the default object (ie "cube.obj")
```
> python3 ./src/main.py
```

- To select an object to load at startup 

```
> python3 ./src/main.py "objectname"
```
For Example to load suzanne as an object we would type python ./src/main.py "suzanne.obj"

**Note**: Step 3 should work on both a windows and linux distribution outside of a virtual environment 
provided the correct packages are installed.

**Note 2**: You can try use the setup desribed in the initial ReadMe provided. If you can get it 
working for the base skeleton provided it should work for mine as well. 


## Key Presses
 
The appropriate Key presses to control the program

Task | Keys |
--- | --- | 
Colour | c Key - cycles through colours (White, Red, Green, Blue) |
Translate along Y axis | Up and Down Keys  |
Translate along X axis | Left and Right Keys |
Scale Up | + Key  |
Scale Down | - Key |
Rotate along X axis | x Key |
Rotate along Y axis | y Key |
Rotate along Z axis | Z key |
Reset Scene | r Key|
Add another object | a Key |
Quite program | q Key 