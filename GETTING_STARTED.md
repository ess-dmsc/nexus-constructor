# Getting started
Firstly, either download the [latest release](https://github.com/ess-dmsc/nexus-constructor/releases) for your OS and run the executable from the root directory, or run the source (refer to the [README](README.md) for instructions on how to do this).

You will be shown the main window of the application (pictured below) which contains both a list of components and a 3D view visualising the components listed with their respective shape and position. 
The sample component is added by default, and is indicated by the red cube. You can move around the 3D view by using the arrow keys to move, click+drag to pan, and pgup/down to zoom.

![](resources/images/NeXusConstructor_001.png)

By clicking the "Nexus File Layout" tab in the left pane of the window, the NeXus file layout can be shown in a tree structure.

![](resources/images/Selection_002.png)

## Adding components

The "add component" button, found in the layout above the list of components (pictured) can be clicked to open a dialog containing possible fields and options a component may include.

![](resources/images/Selection_003.png)


In this screen, we are given options to set what type of component it is, its type of shape as well as being able to set arbitrary fields.
As well as these options, the NeXus format documentation for the component type selected is shown on the right. This shows the required and optional fields for this type of component and what type of data the field should be.

![](resources/images/AddComponent_004.png)


### Adding a source

To add a source, use the add component window and select "NXsource" from the drop-down containing all of the component types. 

This component will need a name, which correlates to the group name in the NeXus file. In this example, we will name it `source1`.

A source has no geometry in real life as it is the neutron beam itself, so leave the radio button marked as "no shape" checked.

As you can see highlighted in the documentation, we can add a field to describe the source. To do this, select the "add field" button. This will add a blank field in the list below it. 

![](resources/images/Selection_005.png)

When inputting the name of the field, in this case we'll add "type", you will see that typing in the name edit will bring up an autocompleter with all of the possible field names. This corresponds to the documentation on the right.

![](resources/images/Tooltip_006.png)


After this, We should set the data type of the field by selecting the type combo and selecting "String". Then, in the value edit, we will enter one of the options specified in the "type" field in the documentation on the right. In this case, lets use `Spallation Neutron Source`

![](resources/images/AddComponent_007.png)

When finished, hit the "add component" button to save it (Note: you can edit this component once saved by selecting it in the list and using the "edit component" button near to the add button). 
You will notice in the 3d view there is a new square which has been added that is black. This would be incorrect in real life, as the source is likely not going to be hitting the sample straight away. To remedy this we should add a transformation to the newly added source component.

#### Setting translation on the source

To the right of the Add component button in the main window toolbar, three additional controls can be used to add transformations to a component. Here we have the option to translate, rotate and link to another component's transformations. 

In this case, we will add a translation, so we can move the source to it's correct position. To do this, first select the source component in the list by clicking it, then click the "add translation" button.

You will see upon adding a new translation the black cube gets shifted to the right immediately. This is because of the default vector specified in the translation. By default the field is disabled, but to edit these fields simply click on it. When finished editing, clicking elsewhere in the list will save the changes. 

![](resources/images/NeXusConstructor_008.png) 

As the source distance will be static and its position will likely not change throughout the experiment, we can set this to a scalar value. A realistic value would have a vector of (0,0,1) and the distance would be `-20m`. Distance units can be changed with the units field next to the value. For this value a float data type should be used, which is the default anyway. 

![](resources/images/NeXusConstructor_009.png)

You will notice after inputting values that the black cube moves behind the sample cube. This is because it is now -20 metres behind it on the z-axis. 

### Adding a detector 

Detectors can be added in the same way as other components, but can contain pixel data in addition to their shape. When a detector or detector module component type is selected and shape information is inputted, the pixel data options will appear.
This is important because some detectors are made up of a grid of pixels, and this needs to be portrayed in the constructor to show the position of each. In our case, we will set the shape type to cylinder and the outcome should look like this:

![](resources/images/AddComponent_010.png) 

#### Setting pixel data

TODO 

#### Loading shape from a CAD file
Alternatively to cylinder shapes, mesh shapes can be used for components to describe their shape. Currently STL and OFF files are supported for mesh geometry. 

To use a mesh file for geometry, select the "Mesh" geometry type. This will show an option to browse for a file. As well as this, units can also be set to change the scale of the geometry.
To test this, there are OFF and STL files in the `tests/` folder.  
TODO: insert a screenshot here

### Adding a chopper

TODO

### Opening and saving file-writer commands 

The constructor can output to a [file-writer command](https://github.com/ess-dmsc/kafka-to-nexus/blob/master/documentation/commands.md) in JSON format, and can also load from these files.
To save to a JSON file, open the file menu and click "Save to filewriter JSON". This will bring up a file dialog in order to save the file. 

TODO: screenshot? 

To open a JSON file, open the file menu and click "Open from filewriter JSON". The constructor will then load in all components and their fields from a given file. 

#### Sending a command to the file-writer

As well as saving the NeXus structure to file, a run start message can be constructed and sent to an instance of the [file-writer]((https://github.com/ess-dmsc/kafka-to-nexus)

TODO: Screenshot

### Opening and saving to NeXus File


