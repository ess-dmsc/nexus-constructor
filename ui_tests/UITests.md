# UI Tests

Due to difficulties combining the UI and testing libraries we use, the Nexus Constructor's
interface isn't able to be easily tested programmatically. The following is a description of the
manual steps that should be taken, and the expected outcomes, to test the user interface.

These tests should be run using a shell environment such as powershell or bash, and not through the
PyCharm IDE, as some types of error that occur in QML will not be printed to the PyCharm console.
None of the following steps should cause a QML error to be printed, and if one is it should be taken
as a failure of that test.

## Starting the application

Run the application (`python nexus-constructor.py` in the root directory).
- The main application window should appear, split into two sections.
- On the left, there should be a QTabWidget labelled "Nexus Structure" containing line edit fields, buttons, checkboxes and 
  a NeXus tree structure with only "entry (NXentry)".
- On the right, there should be an empty instrument view with a Cartesian coordinate system. 
  A small coordinate axis direction indicator should be visible in the lower right corner of the instrument view, 
  which also contains an animation of the beam and its direction.

## Main Window

Increase the width of the window.
* This should cause only the instrument view section to increase in width while the NeXus tree structure section retains a fixed width.
  
Increase the height of the window.
* This should cause both sections in the Main Window to expand in height.

Decrease the width of the window as much as possible.
* This should only affect the width of the instrument view area while the NeXus tree structure retains a fixed width. 
  It should also be confirmed that the instrument view area cannot become any narrower than 300 pixels.

Decrease the height of the window as much as possible.
* This should cause all components beneath the menu bar to reach a minimum height of 100 pixels.

Adjust the Nexus structure QTabWidget width.
* Confirm that a circle is visible in the middle of the right border of the NeXus Structure QTabWidget.
* Clicking and dragging that button left and right should change the width of the box, decreasing the size of the instrument view simultaneously.
  The instrument view and QTabWidget both have a minimum size, which enforces a limit on how much
  the size of the widget can be adjusted by dragging the circle left and right.

## Adding groups and transforms

Press the 'Group' button.
- An editing window should appear.
- It should contain a name input field and description input field.
- It should contain a selector for group type, split into components and groups.
  Components are also groups but with a geometric shape and location.
- It should contain the following radio buttons for component geometry: 'Auto', 'Box', 'Mesh' and 'Cylinder'.
- It should contain the NeXus standard HTML documentation on the right.
- It should contain an 'Add group' and 'Cancel' button in the bottom right.

Select 'NXdetector' as the component type, and 'Mesh' as the geometry type.
- It should not be possible to select 'Repeated Single Pixel Shape', 'Entire Shape', 'No Pixels' as the pixel types.

Select 'Detector' and 'Mesh' as geometry.
- The window should show controls for editing the properties of this new detector.

Click the 'Browse...' button next to the 'CAD file:' textbox.
Open cube_colored.off from the repo's `~/tests` directory. When prompted, select "cm" as unit.
- Choosing 'Entire shape' should populate with 6 empty numbered table columns in a scrollable list.
The first column in the table should be 'Pixel ID for face #0:', and the last one 'Pixel ID for face #5:'.
- Switch to 'No Pixels' and name the 'NXdetector' to detector. Press the 'Add group' button that now should be enabled.
- The NeXus tree structure should now be populated with a 'detector (NXdetector)' child to 'entry (NXentry)'.
- Select the 'detector (NXdetector)' in the tree. The zoom button should be enabled. Press it and you should be able 
to see a colored and slightly tilted cube.
- When the 'detector (NXdetector)' in the NeXus tree is expanded, a 'shape (NXoff_geometry)' should be a child of it.
- Expanding the 'shape (NXoff_geometry)' should show three datasets: 'winding_order', 'faces' and 'vertices'.
- Mark the 'detector (NXdetector)' in the tree again and click the Translation button. That should have created
a 'transformation (NXtransformations)' child to the detector component in the NeXus tree structure.
Double click the 'translation' child of the transformations group and add 0.5 m in the 'Distance' input field.
- Confirm that the cube has moved in the z-direction by again pressing the 'Zoom' button for the detector component.

Select 'entry (NXentry)' in the tree and click the 'Group' button again.
- Select 'Monitor' as group type under 'Components', name it 'monitor' and select 'Cylinder' as geometry.
- Instead of the file selector controls of before, a 'Cylinder options' section should be present.
- It should contain text boxes for height, radius, and x, y, z components of the Cartesian coordinate system.
- Set the cylinders axis direction to (x=1, y=1, z=0), its height to 3, its radius to 1 and unit to "cm". 
  Finally, press the 'Add group' button.
- Now, Add a translation with values (x=-2.5, y=0.5, z=-0.5) to 'monitor (NXmonitor)' under 'entry (NXentry)'.
- Add a rotation, of 315 degrees around axis (x=0, y=0, z=1).
- A cylinder should appear in the 3D view. One flat end should be flush with the leftmost side of
the red sample cube, with center in the rear upper corner.
- The other face should be flush with the right most side of the green detector cube.
- The cylinders radius should intersect the upper edges of the cubes front faces, and the rear edges
of the cubes bottom faces.

## Validating Component Names

Select 'entry (NXentry)' in the tree and click the 'Group' button.
Now create and add a 'NXsample' with the name 'Sample' by choosing 'NXSample from the group type list.
Add another group under 'entry (NXentry)'.
Select a Cylinder geometry and leave the other options untouched.  
Try to name this new component "Sample".
- The text field will accept the name "Sampl"  
- Once you try to type in the remaining "e", the line edit will turn red.
- Placing your mouse over the line edit will show a message saying that group name of a group must be unique
  for all groups with the same parent group.
- Change the name to "Sample2", and the line edit should turn white again.
It should now be possible to add another sample by setting the nexus class to 'NXSample'
Expand the component details box in the left-hand-side of the main window.  
- Repeat the steps above, and you should observe the same behaviour.

## Validating Units 

Click the 'Add component' button. 
Set the component name to "Sample3".
Choose the group type as 'NXsample' again.
Set the geometry to a mesh file.
Click the 'Browse...' button next to the 'CAD file:' textbox.  
Open cube.off from the repo's `~/tests` directory.  
- The 'OK' button on the 'Select Units' window will start out enabled because the default units are valid.

Enter gibberish into the unit text field.
- The units line edit should turn red.
- The 'OK' button will be disabled.
- Placing your mouse over the red line edit will cause an invalid units message to appear.

Replace the gibberish with some valid units.
- The red line edit will turn back to white, and the mouse-over message will no longer be accessible.
- The 'OK' button will become enabled again.

## Transformations

First and foremost, add two component groups to the NeXus tree under 'entry (NXentry)',
The two components should be of type NXsample and called "my_sample" and "other_sample".

Add a rotation and translation to my_sample, by first clicking the "Rotation" button and then
the "Translation" button. 
- There should now be a 'transformations (NXtransformations)' under the "my_sample" component group.
- Expanding the transformations group should show a rotation widget and a translation widget, in that order.
- The "depends_on" in the rotation widget should say "/entry/my_sample/transformations/translation".

Put the values 45 degrees and 2 m in the rotation and translation widgets, respectively.
- The instrument view should be updated accordingly. First a rotation around the x-axis
  followed by a translation in the z-direction.

Now add a translation to the "other_sample" component group. Put the value -1 in the translation widget.
- Confirm that the instrument view updates the coordinates of other_sample to (0, 0, -1).

Add a "Link" to the transformations by for example selecting "other_sample" and clicking the Link button.
- Confirm that a Link widget is added to the transformations group of "other_sample".

Select the "my_sample" component in the list under "Select component".
- Once leaving the Link widget, confirm that the instrument view now clearly indicates a dependency
from "other_sample" to "my_sample". 
  - The "depends_on" in the translation widget of the other_sample should now
  show "/entry/my_sample/transformations/rotation".
    
Rename rotation transformation in "my_sample" to "my_rotation" and confirm that the "depends_on" is
updated correctly in "other_sample".

Finally, make sure that deleting the transformations groups in both sample components
puts them in the original spot in the origin, i.e. (0, 0, 0).

## Saving to file and loading from file

Create a NeXus tree structure that contains the following structure groups under 'entry (NXentry)':

 - instrument (NXinstrument)
 - sample (NXsample)

Add a translation to sample of -1 in the z-direction.
Define the geometry of the sample to a box with the dimension (0.2, 0.5, 1.0) meters.

In the instrument group add following groups:
- detector (NXdetector)
- monitor (NXmonitor)
- chopper (NXdisk_chopper) with 'slits': 1, radius: 0.4 m, slit_edges to (-45, 45) degrees and
slit_height to 0.1 m.
  
Try to add some appropriate transformations to each component in the instrument group.
  
Now save the file as "my_file.json" in some directory of your choice.
Load it and confirm that the instrument you created above is loaded in the NeXus tree view and
rendered correctly in the instrument view window.
Re-save the file into "my_file_2.json" and compare it to "my_file.json" in a text editor.
The content of the files should be the same.

## Removing a group from the instrument view and NeXus tree view

In the instrument you created above, add a group 'wrong_sample (NXsample)' under 'entry (NXentry)'
Add a translation -10 to the "wrong_sample". Try to delete the "wrong_sample" group and confirm
that it disappears both from the NeXus tree view, and the instrument 3D view.

## Drag and drop groups in the NeXus tree

Load your "my_file.json" from above and add a group "monitor_2" of type NXmonitor under 'entry (NXentry)'.
This is of course wrong, the monitor should be put under 'instrument (NXinstrument)'.
Correct this by selecting the "monitor_2" group and dragging it from the entry group to the instrument group
by dragging it inside the 'instrument (NXinstrument)' structure in the tree view.
Confirm that this actually worked correctly.
