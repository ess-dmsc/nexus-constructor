# UI Tests

Due to difficulties combining the UI and testing libraries we use, the Nexus Constructor's
interface isn't able to be easily tested programaticaly. The following are a description of the
manual steps that should be taken, and the expected outcomes, to test the user interface.

These tests should be run using a shell environment such as powershell or bash, and not through the
PyCharm IDE, as some types of error that occur in QML will not be printed to the PyCharm console.
None of the following steps should cause a QML error to be printed, and if one is it should be taken
as a failure of that test.

## Starting the application

Run the application (`python main.py` in the root directory).
- The main application window should appear, split into three sections.
- On the left should be a box labelled "Components" containing a single smaller box titled "Sample".
- In the center should be an animated neutron beam, pointing into a red cube.
- To the right should be a scrollable JSON area.

## Main Window

Increase the width of the window.
* This should cause only the (center) Instrument View to increase in width while the other components retain a fixed width.

Increase the height of the window.
* This should cause all elements in the Main Window to expand in height.

Decrease the width of the window as much as possible.
* This should only affect the width of the Instrument View area while the other components retain a fixed width. It should also be noticed that the Instrument View area cannot become any narrower than 300 pixels.

Decrease the height of the window as much as possible.
* This should cause all components beneath the menu bar to reach a minimum height of 100 pixels.

## JSON Display

With the application open, click on the 'Sample' box in the 'Components' pane.
- It should expand, showing a text field to edit the name.

Change the value of the name field, and press enter.
- The JSON display should automatically update to show the name value on the relevant line.

Open the 'JSON' menu at the top of the application window, and click the "Show Nexus Constructor
JSON" radio button.
- The format of the JSON display should change, but the new name value should still be contained in
it.

Update the name of the sample to a new value as before.
- This change should also apply automatically to the JSON display.

Open the 'JSON' menu again, and click the "Hide JSON display" radio button.
- The JSON display should disappear, with its space in the window being taken by the 3D
visualisation area.

Open the 'JSON' menu, and reselect "Show Nexus FileWriter JSON".
- The JSON display should reappear, containing JSON in the original format, with the current name
value.

Click on the opening line in the JSON display `{`
- The initial line should be replaced with `{...}`
- All other lines should be hidden.

Click on the `{...}` line.
- The trailing `...}` should vanish from the first line.
- The hidden lines should reappear.

Reset the sample's name to 'Sample'.

## Adding components and transforms

Press the 'Add component' button.
- The "Add component" window should appear.
- It should contain a selector for component type.
- It should contain the following radio buttons for component geometry: 'Mesh', 'Cylinder' and 'None'.
- It should contain a set of radio buttons for pixel layout, 'Single ID', 'Repeatable grid', 'Face
mapped mesh' and 'None'.
- It should contain a 'Continue' button at the bottom.

Select 'Detector' as the component type, and 'Mesh' as the geometry type.
- It should not be possible to select 'Single ID' or 'None' as the pixel types.

Select 'Cylinder' as the geometry type.
- It should now also not be possible to select 'Face mapped mesh' as a pixel type.

Select 'Monitor' as the component type.
- Regardless of selected geometry type, only 'Single ID' can be selected as pixel type.

Select any other component type (except 'Monitor').
- Regardless of selected geometry type (except 'None'), only 'None' can be selected as pixel type.

Select 'Detector', 'Mesh', and 'Face mapped mesh'. Click 'Continue'.
- The window should show controls for editing the properties of this new detector.
- The window should automatically resize to fit these new controls.

Click the 'Choose file' button next to the 'Geometry file:' textbox.
Open cube.stl from the repo's `~/tests` directory.
- The 'Pixel mapping' area should populate with 12 empty numbered textboxes in a scrollable list.

Enter '1' into the first such box. Click again on the 'Choose file' button, and open cube.off from
the repo's `~/tests` directory. When prompted, select "cm" as unit.
- The 'Pixel mapping' area should re-populate with 6 empty numbered textboxes in a scrollable list.

Click the 'add translation' button in the 'Transform:' section.
- A box should appear containing textboxes for the translations name and x, y, z components, along
with 'move up', 'move down' and 'delete' buttons.
- The window should increase its size to fit these controls.

Enter a '2' in the translate's x field, and 'cube transform' in the translate's name field.

Enter 'Cube detector' in the name field.
Click the 'Add' button.
- The window should close.
- The main windows 'components' section should contain a second box, reading 'Name:Cube detector'.
- A green cube should be visible in the 3D view. It should be to the right of the sample's red cube,
with a gap between them equal to one of their widths.

Click the 'Add Component' button.
Select 'Monitor' as component type, and 'Cylinder' as geometry.
Click 'Continue'.
- Instead of the file selector controls of before, a 'Cylinder Geometry' section should be present.
- It should contain textboxes for height, radius, and x, y, z components of axis direction.
- A 'pixel data' section should contain a single textbox for detector id.

Set the cylinders axis direction to (x=1, y=1, z=0), its height to 3, its radius to 1 and unit to "cm".
Add a translation with values (x=-2.5, y=0.5, z=-0.5).
Add a rotation, of 315 degrees around axis (x=0, y=0, z=1).
Set the 'Transform parent' dropdowns to 'Cube Detector' and 'cube transform'.
Click 'Add'.
- The add component window will close.
- A cylinder should appear in the 3D view. One flat end should be flush with the leftmost side of
the red sample cube, with center in the rear upper corner.
- The other face should be flush with the right most side of the green detector cube.
- The cylinders radius should intersect the upper edges of the cubes front faces, and the rear edges
of the cubes bottom faces.

## Validating Component Names

Click the 'Add component' button.  
Select a Cylinder geometry and leave the other options untouched.  
Try to name this new component "Sample".
- The text field will accept the name "Sampl"  
- Once you try to type in the remaining "e" a red cross will appear.
- Placing your mouse over the cross will show a message saying that component names must be unique.

Remove focus from the text field by selecting a different field or by moving the mouse out of the window.
- The red cross disappear and the message will no longer be accessible.
- The component name will still be "Sampl".

Change the name back to its default and click "Add" without changing any of the other options.  
Expand the component details box in the left-hand-side of the main window.  
- Repeat the steps above and you should observe the same behaviour.

Change the name back to its default again.  
Expand the component details box.  
Click the 'Full editor' button.  
- Repeat the steps above and you should observe the same behaviour.

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

## Removing components

Set Monitor's transform parent to 'Cube Detector'.
- Cube Detector's delete button should grey out, and clicking it result in nothing.

Click Monitor's delete button.
- Monitor should vanish from the components list.
- The cylinder in the 3D view should vanish too.
- Cube Detector's delete button should be enabled.

Click Cube Detector's delete button.
- It should also disappear from the components list.
- It's green cube should no longer be in the visualisation.

## Sample details

- There should be no delete button or transform controls in the Sample box in the components list.
- Clicking it's full editor button will open an editor window without pixel or transform fields.

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
