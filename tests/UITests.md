# UI Tests

Due to difficulties combining the UI and testing libraries we use, the Nexus Constructor's
interface isn't able to be easily tested programmatically. The following is a description of the
manual steps that should be taken, and the expected outcomes, to test the user interface.

These tests should be run using a shell environment such as powershell or bash, and not through the
PyCharm IDE, as some types of error that occur in QML will not be printed to the PyCharm console.
None of the following steps should cause a QML error to be printed, and if one is it should be taken
as a failure of that test.

## Starting the application

Run the application (`python main.py` in the root directory).
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
The first column in the table should be 'Pixel ID for face #0:' and the last one 'Pixel ID for face #5:'.
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
- It should contain textboxes for height, radius, and x, y, z components of the Cartesian coordinate system.
- Set the cylinders axis direction to (x=1, y=1, z=0), its height to 3, its radius to 1 and unit to "cm". 
  Finally, press the 'Add group' button.
- Now, Add a translation with values (x=-2.5, y=0.5, z=-0.5) to 'monitor (NXmonitor)' under 'entry (NXentry)'.
- Add a rotation, of 315 degrees around axis (x=0, y=0, z=1).
- A cylinder should appear in the 3D view. One flat end should be flush with the leftmost side of
the red sample cube, with center in the rear upper corner.
- The other face should be flush with the right most side of the green detector cube.
- The cylinders radius should intersect the upper edges of the cubes front faces, and the rear edges
of the cubes bottom faces.

## Validating Group Names

Click the 'Group' button after selecting 'entry (NXentry)' in the NeXus tree view.  
- Create an 'NXsample' component called "Sample" under 'entry (NXentry)'.
- Now create another 'NXsample' and try to name this new component "Sample" as well.
- The text field will accept the name "Sampl"  
- Once you try to type in the remaining "e" the line edit should turn red.
- Placing your mouse over the line edit will show a message saying that group name is not valid, 
  and it will suggest naming it "Sample1" instead.
- It should not be possible to press 'Add group' while the line edit is colored red.
- The rule is that groups on the save level must have unique names. We should however be able 
  to create an 'NXinstrument' under the 'entry (NXentry)' node and under the instrument create a
  'NXsample' named Sample. Confirm that this is in reality the case!

## Validating Units 

Click the 'Add component' button.  
Press 'Continue' without changing any of the other options.  
Click the 'Choose file' button next to the 'Geometry file:' textbox.  
Open cube.stl from the repo's `~/tests` directory.  
- The 'OK' button on the 'Select Units' window will start out enabled because the default units are valid.

Enter gibberish into the unit text field.
- A red cross will appear next to the text field.
- The 'OK' button will be disabled.
- Placing your mouse over the red cross will cause an invalid units message to appear.

Replace the gibberish with some valid units.
- The red cross will disappear and the mouse-over message will no longer be accessible.
- The 'OK' button will become enabled again.

Close the 'Select Units' and 'Add Detector' windows.  
Click 'Add component' again.  
Select Cylinder geometry and click 'Continue'. The other options can be left as their defaults.
- The 'Add' button will start out enabled because the default units are valid.

Enter gibberish into the unit text field.
- A red cross will appear next to the text field.
- The 'Add' button will be disabled.
- Placing your mouse over the red cross will cause an invalid units message to appear.

Replace the gibberish with some valid units.
- The red cross will disappear and the mouse-over message will no longer be accessible.
- The 'Add' button will become enabled again.

## Transform ordering

In the Components section, click the box labelled 'Name:Cube detector'.
- The box should expand revealing name and transform editors, as well as 'Full editor' and 'delete'
buttons.
- The components delete button, and the delete button of its translation should be disabled and
greyed out.
- Hovering over these buttons should display a tooltip explaining why.


In the Components section, click the box labelled 'Name:Monitor'.
- It should expand, revealing a textbox for editing the component name, transform controls,
containing the translate and rotate values entered in the previous screen, and buttons marked 'Full
editor' and 'delete'.
- The translate should be above the rotate.

Rename the transform in 'Cube detector' to just 'translate'.
- The name change should be reflected in 'Monitor's second transform parent dropdown.

Set the monitors 'transform parent' to 'Sample'.
- The graphic of the cylinder should align its right face with the right face of the sample cube.
- The delete buttons of 'Cube detector' and its transform should no longer be greyed out or show
tooltips on hover.

Click the 'Move up' button on the translate in Monitor.
- Nothing should happen.

Click the 'Move down' button on the rotate in Monitor.
- Nothing should happen.

Click the 'Move down' button on the translate in Monitor.
- It should swap places with the rotate.
- The cylinder in the visualisation should move upwards and to the right.

Click the 'Move up' button on the translate (now at the bottom of the list) in Monitor.
- It should swap places with the rotate.
- The cylinder in the visualisation should move back down and left to align again with the cube.

Click the 'Delete' button on the rotation.
- The rotation should disappear from the transforms section.
- The cylinder visualisation should now point upwards and to the right, with its lower/left end face
still level with the upper rear of the cubes.

## Editor window

Click the 'Full editor' button for the Monitor.
- A component editor window should appear, containing the same transform values as the main window,
and the cylinder geometry/pixel data values entered earlier.

Add an exclamation mark to the monitor name in the new window, and tab out of the textbox.
- The updated name should be present in the main window too.

Remove the ! in the main window's textbox, and tab out of the textbox.
- The editor window's textbox should reflect the change.

Click the 'add rotation' button in the editor window.
- A set of rotation editor fields should appear in both windows.

Click the new rotations delete button in the main window.
- The fields should disappear from both windows.

Set the radius of the cylinder to 2.
- The cylinder's visualisation in the main window should double in radius.

## Saving to file

Close the editor window.
In the menu bar, select 'File' > 'Save', and save to a new file called 'gc_ui_test.json'.
In the menu bar, select 'File' > 'Export to FileWriter', and save to a new file called
'fw_ui_test.json'.
In the menu bar, select 'File' > 'Export to NeXus file', and save to a new file called
'ui_test.nxs'.
- These files should have all been created on disk.

Open gc_ui_test.json in a text editor.
- It should contain a json object at its root, with a child element called 'components'.
- Searching the document should return one hit for each of the following:
  - `"name": "Cube detector"`
  - `"name": "Sample"`
  - `"name": "Monitor"`

Open fw_ui_test.json in a text editor.
- It should contain a json object at its root, with a child element called 'nexus_structure'.
- Searching the document should return one hit for each of the following:
  - `"name": "Cube detector"`
  - `"name": "Sample"`
  - `"name": "Monitor"`

Open ui_test.nxs in HDFView.
- It should contain groups called 'Sample', 'Monitor', and 'instrument' as children of the root
group 'entry'.
- 'instrument' should contain another group called 'Cube detector'.

## Removing groups

Set Monitor's transform parent to 'Cube Detector'.
- Cube Detector's delete button should grey out, and clicking it result in nothing.

Click Monitor's delete button.
- Monitor should vanish from the components list.
- The cylinder in the 3D view should vanish too.
- Cube Detector's delete button should be enabled.

Click Cube Detector's delete button.
- It should also disappear from the components list.
- It's green cube should no longer be in the visualisation.

## Loading json

Change the sample's name to 'lone sample'.
In the menu bar, select 'File' > 'Open' and select 'gc_ui_test.json'.
- Three components should exist in the components box, named 'Sample', 'Cube Detector', and
'Monitor'.
- The green detector cube should reappear a cube's distance to the sample cube's right.
- The monitor cylinder should reappear with its larger radius, to the left of the sample cube,
pointing up and to the right.

Close and re-open the Nexus Constructor.
In the menu bar, select 'File' > 'Open' and select 'fw_ui_test.json'.
- Three components should exist in the components box, named 'Sample', 'Cube Detector', and
'Monitor'.
- The green detector cube should reappear a cube's distance to the sample cube's right.
- The monitor cylinder should reappear with its larger radius, to the left of the sample cube,
pointing up and to the right.

## Other validation

Expand the component sections for Cube detector and Monitor.
- The first 'transform parent' dropdown in Cube detector should only show 'Sample' and
'Monitor' as options.
- The first 'transform parent' dropdown in Monitor should only show 'Sample' and 'Cube
Detector' as options.

Set the transform parent of Monitor to Cube Detector.
Attempt to set Cube Detector's transform parent to Monitor.
- The drop down in Cube Detector should revert to its previous value.
- Tooltext should appear explaining that this loop is invalid.
