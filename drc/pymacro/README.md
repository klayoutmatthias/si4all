# DRC Python Macro

This directory contains the Klayout Macro implementation using Python API, for Design Rule Check (DRC).
The supported checks follow the same template as those in `drc.lydrc`.
However, the output dumping method is different.
Here, instead of putting the errors in a database, they are dumped as layout layer objects. 
These layers are named after the errors and make it easier to locate the errors (by enabling individual error layers and concered layers from original layout, at a time).

## Input Format 

The script can be executed from Klayout macro environment or the command-line. 
It includes following variables, which can be modified from within the script: 
1. `gds_path` : specifies the path to the original GDSII file input for DRC check.  
2. `drawing_layers` : an array of available layer names in the given GDSII file. 
Note, the order & number of layers in gds file, must match the corresponding entities in this array. 
3. `error_layers` : an array of error layer names. 
These names are used with the error layers dumped into a newer GDSII file created with the name `<design>_drc.gds`. 
The procedure is - check the design for a DRC check 'A', dump the output into a new layer, attach this layer with name 'Check_A'.
These names are used to create the .lyp file, which can be loaded with the `<design>_drc.gds` file in Klayout.
As these names & error dumping are detached, the layer name can be changed easily, </br>
for ex. 'Check_A1' & 'Check_A2' -> 'Width_check_A' & 'Area_check_A', without affecting the code.
4. `unit` : unit in which all of the dimensions are given

## Output Format 

The output of DRC is another GDSII format file, named as `<design>_drc.gds` & a layout properties file named `<design>.lyp`. 
