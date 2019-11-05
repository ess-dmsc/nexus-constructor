from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import QSpinBox, QDoubleSpinBox, QListWidgetItem
import numpy as np

from nexus_constructor.component.component import Component
from nexus_constructor.geometry.geometry_loader import load_geometry
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, CountDirection, Corner
from nexus_constructor.pixel_mapping_widget import PixelMappingWidget
from nexus_constructor.validators import PixelValidator
from ui.pixel_options import Ui_PixelOptionsWidget

RED_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #f6989d }"
WHITE_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #FFFFFF }"

BOTTOM_LEFT_TEXT = "Bottom Left"
BOTTOM_RIGHT_TEXT = "Bottom Right"
TOP_LEFT_TEXT = "Top Left"
TOP_RIGHT_TEXT = "Top Right"


def check_data_is_an_array(data) -> bool:
    """
    At the moment it appears as though a scalar can still be returned as an array when using `get_field_value` (though
    it could just be me doing the wrong thing). This function checks if an array contains more than one value so that
    Pixel Data can be edited in the case of a Single Shape.
    :param data: The data value from the NeXus file.
    :return: True if the data is a scalar or an array containing a single value, False otherwise.
    """
    if type(data) is not np.ndarray:
        return False

    return data.size > 1


class PixelOptions(Ui_PixelOptionsWidget, QObject):
    def __init__(self):

        QObject.__init__(self)

        self.pixel_mapping_widgets = []

        # Dictionaries that map user-input to known pixel grid options. Used when creating the PixelGrid.
        self.count_direction = {
            "Rows": CountDirection.ROW,
            "Columns": CountDirection.COLUMN,
        }
        self.initial_count_corner = {
            BOTTOM_LEFT_TEXT: Corner.BOTTOM_LEFT,
            BOTTOM_RIGHT_TEXT: Corner.BOTTOM_RIGHT,
            TOP_LEFT_TEXT: Corner.TOP_LEFT,
            TOP_RIGHT_TEXT: Corner.TOP_RIGHT,
        }

        self.pixel_validator = None
        self.current_mapping_filename = None

    def setupUi(self, parent_widget):

        super().setupUi(parent_widget)

        self.pixel_validator = PixelValidator(
            parent_widget,
            self.single_pixel_radio_button,
            self.entire_shape_radio_button,
        )

        # Have the radio buttons change the visibility of the pixel options
        self.setup_visibility_signals()

        # Have the pixel mapping button populate the list widget if necessary
        self.entire_shape_radio_button.clicked.connect(
            self.generate_pixel_mapping_if_required
        )

        # Setup the pixel grid behaviour
        self.setup_pixel_grid_options()

        # Cause the overall Pixel Options validity to change when a different type of Pixel Layout has been selected
        self.single_pixel_radio_button.clicked.connect(self.update_pixel_input_validity)
        self.entire_shape_radio_button.clicked.connect(self.update_pixel_input_validity)
        self.no_pixels_button.clicked.connect(self.update_pixel_input_validity)

        # Update the validity
        self.update_pixel_input_validity()

    def fill_existing_entries(self, component_to_edit: Component):
        """
        Populate the pixel fields based on what is already stored in the NeXus file.
        """
        if component_to_edit.get_field("x_pixel_offset") is not None:
            self.single_pixel_radio_button.setChecked(True)
            self.update_pixel_layout_visibility(True, False)
            self._fill_single_pixel_fields(component_to_edit)

        elif component_to_edit.get_field("detector_number") is not None:
            self.entire_shape_radio_button.setChecked(True)
            self.update_pixel_layout_visibility(False, True)
            self._fill_entire_shape_fields(component_to_edit)

        else:
            self.no_pixels_button.setChecked(True)
            self.pixel_options_stack.setVisible(False)

    def _fill_single_pixel_fields(self, component_to_edit: Component):

        x_pixel_offset = component_to_edit.get_field("x_pixel_offset")
        y_pixel_offset = component_to_edit.get_field("y_pixel_offset")
        detector_numbers = component_to_edit.get_field("detector_number")

        if check_data_is_an_array(x_pixel_offset):

            # If the pixel offset information is multidimensional then extra steps need to be taken to restore the info
            self._fill_row_information(y_pixel_offset)
            self._fill_column_information(x_pixel_offset)
            self._fill_detector_number_information(detector_numbers)

        else:

            # If the pixel offset information represents a single pixel
            self.first_id_spin_box.setValue(detector_numbers)

    def _fill_detector_number_information(self, detector_numbers: np.ndarray):

        first_id = np.amin(detector_numbers)
        self.first_id_spin_box.setValue(first_id)

        first_id_index = np.where(detector_numbers == first_id)
        first_id_index = (first_id_index[0][0], first_id_index[1][0])

        if first_id_index == (0, 0):
            self.start_counting_combo_box.setCurrentText(TOP_LEFT_TEXT)
        elif first_id_index[0] == 0:
            self.start_counting_combo_box.setCurrentText(TOP_RIGHT_TEXT)
        elif first_id_index[1] == 0:
            self.start_counting_combo_box.setCurrentText(BOTTOM_LEFT_TEXT)
        else:
            self.start_counting_combo_box.setCurrentText(BOTTOM_RIGHT_TEXT)

    def _fill_row_information(self, y_pixel_offset: np.ndarray):

        n_rows = y_pixel_offset.shape[0]
        self.row_count_spin_box.setValue(n_rows)

        row_height = np.abs(y_pixel_offset[0][0] - y_pixel_offset[1][0])
        self.row_height_spin_box.setValue(row_height)

    def _fill_column_information(self, x_pixel_offset: np.ndarray):

        n_cols = x_pixel_offset.shape[1]
        self.column_count_spin_box.setValue(n_cols)

        col_width = np.abs(x_pixel_offset[0][1] - x_pixel_offset[0][0])
        self.column_width_spin_box.setValue(col_width)

    def _fill_entire_shape_fields(self, component_to_edit: Component):
        pass

    def get_current_mapping_filename(self):
        """
        Retrieves the filename of the mesh that has been used to generate the list of pixel mapping widgets. Used in
        order to prevent creating the same list twice should the same file be selected twice with the file dialog.
        :return: The filename of the mesh.
        """
        return self.current_mapping_filename

    def setup_visibility_signals(self):
        """
        Instructs the Single Pixel/Entire Shape/No Pixels buttons to alter the visibility of items in the
        PixelOptionsWidget.
        """
        self.single_pixel_radio_button.clicked.connect(
            lambda: self.update_pixel_layout_visibility(True, False)
        )
        self.entire_shape_radio_button.clicked.connect(
            lambda: self.update_pixel_layout_visibility(False, True)
        )
        self.no_pixels_button.clicked.connect(self.hide_pixel_options_stack)

    def setup_pixel_grid_options(self):
        """
        Deals with connecting the pixel grid's signals to methods that check for validity or enforce certain rules about
        the input.
        """

        # Make the column and row count spin boxes in the Pixel Grid trigger a validity update
        self.row_count_spin_box.valueChanged.connect(self.update_pixel_grid_validity)
        self.column_count_spin_box.valueChanged.connect(self.update_pixel_grid_validity)

        # Make the row/column count being set to zero cause its matching distance field to become disabled
        self.column_count_spin_box.valueChanged.connect(
            lambda: self.disable_or_enable_distance_field(
                self.column_count_spin_box, self.column_width_spin_box
            )
        )
        self.row_count_spin_box.valueChanged.connect(
            lambda: self.disable_or_enable_distance_field(
                self.row_count_spin_box, self.row_height_spin_box
            )
        )

        # Manually add options to the "Count first along" combo box. This is done here because inserting these options
        # through Qt Designer doesn't work.
        self.count_first_combo_box.addItems(list(self.count_direction.keys()))

    def get_validator(self):
        """
        :return: The PixelOptions' PixelValidator. This is needed in the AddComponentDialog so that it has knowledge
        of the PixelOptions' validity status.
        """
        return self.pixel_validator

    def generate_pixel_mapping_if_required(self):
        """
        Informs the AddComponentDialog that the "Entire Shape" button has been pressed. This then causes the
        AddComponentDialog to check if a new and valid file has been given. If these conditions are met then the
        AddComponentDialog will call the method for populating the pixel mapping list. If these conditions are not meant
        then the list will remain empty.
        """
        if self.pixel_mapping_list_widget.count() == 0:
            self.pixel_mapping_button_pressed.emit()

    @staticmethod
    def disable_or_enable_distance_field(
        count_spin_box: QSpinBox, distance_spin_box: QDoubleSpinBox
    ):
        """
        Disables or enabled the matching distance field of the row/column count spin box in the pixel grid options
        depending on if the number of rows/columns has been set to zero.
        :param count_spin_box: The row/column count spin box.
        :param distance_spin_box: The matching row height/column width spin box.
        """
        distance_spin_box.setEnabled(count_spin_box.value() != 0)

    def update_pixel_grid_validity(self):
        """
        Update the OK Validator to reflect the validity of the current Pixel Grid input. A PixelGrid is valid provided
        that the rows or columns have a non-zero value. It is invalid if both are zero. The Spin Boxes enforce
        everything else so this is the only check required.
        """
        self.pixel_validator.set_pixel_grid_valid(
            not (
                self.row_count_spin_box.value() == 0
                and self.column_count_spin_box.value() == 0
            )
        )

    def update_pixel_layout_visibility(self, pixel_grid: bool, pixel_mapping: bool):
        """
        Changes the visibility of the Pixel Options stack. This displays either the Pixel Grid or the Pixel Mapping.
        :param pixel_grid: Bool indicating whether or not to show the pixel grid options.
        :param pixel_mapping: Bool indicating whether or not to show the pixel mapping options.
        """
        self.pixel_options_stack.setVisible(True)

        if pixel_grid:
            self.pixel_options_stack.setCurrentIndex(0)
        elif pixel_mapping:
            self.pixel_options_stack.setCurrentIndex(1)

    def populate_pixel_mapping_list_with_mesh(self, filename: str):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file for
        an NXoff_geometry.
        """
        if self.pixel_mapping_not_visible():
            return

        n_faces = self.get_number_of_faces_from_mesh_file(filename)

        self.reset_pixel_mapping_list()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        self.create_pixel_mapping_list(n_faces, "face")

        # Record the filename of the current mapping to prevent the widgets from being created twice
        self.current_mapping_filename = filename

    def populate_pixel_mapping_list_with_cylinder_number(self, cylinder_number: int):
        """
        Populates the pixel mapping list based on a number of cylinders for the NXcylindrical_geometry.
        :param cylinder_number: The number of cylinders.
        """
        if self.pixel_mapping_not_visible():
            return

        # Set the mapping filename to None as cylinder mappings are not based on a mesh file.
        self.current_mapping_filename = None
        self.reset_pixel_mapping_list()
        self.create_pixel_mapping_list(cylinder_number, "cylinder")

    @staticmethod
    def get_number_of_faces_from_mesh_file(filename: str):
        """
        Creates a temporary geometry and uses this is order to determine the number of faces in the file.
        :param filename: The filename for the mesh.
        :return: The number of faces in the mesh.
        """
        temp_geometry = load_geometry(filename, "m")
        return len(temp_geometry.faces)

    def hide_pixel_options_stack(self):
        """
        Conceals the Pixel Options stack (containing the Pixel Grid and Pixel Mapping options). This takes place when
        the No Pixels button has been pressed.
        """
        self.pixel_options_stack.setVisible(False)

    def get_pixel_mapping_ids(self):
        """
        :return: A list of the IDs for the current PixelMappingWidgets.
        """
        return [
            pixel_mapping_widget.get_id()
            for pixel_mapping_widget in self.pixel_mapping_widgets
        ]

    def update_pixel_mapping_validity(self):
        """
        Checks that at least one ID has been given in the Pixel Mapping and then updates the PixelValidator.
        """
        nonempty_ids = [
            widget.get_id() is not None for widget in self.pixel_mapping_widgets
        ]
        self.pixel_validator.set_pixel_mapping_valid(any(nonempty_ids))

    def generate_pixel_data(self):
        """
        Creates the appropriate PixelData object depending on user selection then gives it the information that the
        user entered in the relevant fields. If the "No Pixel" button has been pressed then the method returns None.
        In the case of a PixelGrid where either rows/columns has been set to zero, this also causes the matching
        distance value to be recorded as zero.
        :return: A PixelData object or None.
        """
        if self.single_pixel_radio_button.isChecked():

            rows = self.row_count_spin_box.value()
            row_height = self.row_height_spin_box.value()

            if rows == 0:
                row_height = 0

            columns = self.column_count_spin_box.value()
            col_width = self.column_width_spin_box.value()

            if columns == 0:
                col_width = 0

            return PixelGrid(
                rows=rows,
                columns=columns,
                row_height=row_height,
                col_width=col_width,
                first_id=self.first_id_spin_box.value(),
                count_direction=self.count_direction[
                    self.count_first_combo_box.currentText()
                ],
                initial_count_corner=self.initial_count_corner[
                    self.start_counting_combo_box.currentText()
                ],
            )

        if self.entire_shape_radio_button.isChecked():
            return PixelMapping(self.get_pixel_mapping_ids())

    def update_pixel_input_validity(self):
        """
        Changes the state of the OK Validator depending on whether or not the pixel input is valid. If The No Pixel
        option has been selected then there is nothing to do outside of calling `validate_pixels` again.
        """
        if self.single_pixel_radio_button.isChecked():
            self.update_pixel_grid_validity()
        elif self.entire_shape_radio_button.isChecked():
            self.update_pixel_mapping_validity()
        else:
            self.pixel_validator.inform_ok_validator()

    def pixel_mapping_not_visible(self):
        """
        Checks if the pixel mapping options are visible. This is used to determine if it is necessary to generate a
        pixel mapping list.
        :return: A bool indicating the current index of the PixelOptions stack.
        """
        return self.pixel_options_stack.currentIndex() != 1

    def reset_pixel_mapping_list(self):
        """
        Clear the current pixel mapping list and widget. Used when the mesh file changes in the case of NXoff_geometry,
        when the number of cylinders change in the case of NXcylindrical_geometry, or when the user switches between
        mesh and cylinder.
        """
        self.pixel_mapping_widgets = []
        self.pixel_mapping_list_widget.clear()

    def create_pixel_mapping_list(self, n_items, text):
        """
        Creates a list of pixel mapping widgets.
        :param n_items: The number of widgets to create.
        :param text: The label to be displayed next to the line edit. This is either faces or cylinders.
        """

        for i in range(n_items):
            pixel_mapping_widget = PixelMappingWidget(
                self.pixel_mapping_list_widget, i, text
            )
            pixel_mapping_widget.pixelIDLineEdit.textChanged.connect(
                self.update_pixel_mapping_validity
            )

            # Make sure the list item is as large as the widget
            list_item = QListWidgetItem()
            list_item.setSizeHint(pixel_mapping_widget.sizeHint())

            self.pixel_mapping_list_widget.addItem(list_item)
            self.pixel_mapping_list_widget.setItemWidget(
                list_item, pixel_mapping_widget
            )

            # Keep the PixelMappingWidget so that its ID can be retrieved easily when making a PixelMapping object.
            self.pixel_mapping_widgets.append(pixel_mapping_widget)

    pixel_mapping_button_pressed = Signal()
