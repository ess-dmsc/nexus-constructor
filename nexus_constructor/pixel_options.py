from typing import List, Optional, Tuple

import numpy as np
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QDoubleSpinBox, QMessageBox, QSpinBox, QTableWidgetItem

from nexus_constructor.geometry.geometry_loader import load_geometry
from nexus_constructor.geometry.pixel_data import (
    Corner,
    CountDirection,
    PixelData,
    PixelGrid,
    PixelMapping,
)
from nexus_constructor.model.component import Component
from nexus_constructor.model.geometry import (
    DETECTOR_NUMBER,
    X_PIXEL_OFFSET,
    Y_PIXEL_OFFSET,
    BoxGeometry,
    OFFGeometryNexus,
)
from nexus_constructor.validators import PixelValidator
from ui.pixel_options import Ui_PixelOptionsWidget

BOTTOM_LEFT_TEXT = "Bottom Left"
BOTTOM_RIGHT_TEXT = "Bottom Right"
TOP_LEFT_TEXT = "Top Left"
TOP_RIGHT_TEXT = "Top Right"

PIXEL_GRID_STACK_INDEX = 0
PIXEL_MAPPING_STACK_INDEX = 1

INITIAL_COUNT_CORNER = {
    BOTTOM_LEFT_TEXT: Corner.BOTTOM_LEFT,
    BOTTOM_RIGHT_TEXT: Corner.BOTTOM_RIGHT,
    TOP_LEFT_TEXT: Corner.TOP_LEFT,
    TOP_RIGHT_TEXT: Corner.TOP_RIGHT,
}

ROWS_TEXT = "Rows"
COLUMNS_TEXT = "Columns"

COUNT_DIRECTION = {ROWS_TEXT: CountDirection.ROW, COLUMNS_TEXT: CountDirection.COLUMN}


def data_is_an_array_with_more_than_one_element(data) -> bool:
    """
    At the moment it appears as though a scalar can still be returned as an array when using `get_field_value` (though
    it could just be me doing the wrong thing). This function checks if an array contains more than one value so that
    Pixel Data can be edited in the case of a single Shape.
    :param data: The data value from the NeXus file.
    :return: True if the data is a scalar or an array containing a single value, False otherwise.
    """
    if np.isscalar(data):
        return False

    return data.size > 1


class PixelOptions(Ui_PixelOptionsWidget, QObject):
    def __init__(self):
        QObject.__init__(self)
        self._pixel_validator = None
        self.current_mapping_filename = None

    def setupUi(self, parent_widget):

        super().setupUi(parent_widget)

        self._pixel_validator = PixelValidator(
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

        # Add listener to item changed event in pixel mapping table widget.
        self.pixel_mapping_table_widget.itemChanged.connect(self.item_changed)

    def fill_existing_entries(self, component_to_edit: Component):
        """
        Populate the pixel fields based on what is already stored in the NeXus file.
        """
        self.reset_pixel_mapping_table()

        try:
            component_to_edit.get_field_value(X_PIXEL_OFFSET)
            self.single_pixel_radio_button.setChecked(True)
            self.update_pixel_layout_visibility(True, False)
            self._fill_single_pixel_fields(component_to_edit)
            return
        except AttributeError:
            pass

        try:
            component_to_edit.get_field_value(DETECTOR_NUMBER)
            self.entire_shape_radio_button.setChecked(True)
            self.update_pixel_layout_visibility(False, True)
            self._fill_entire_shape_fields(component_to_edit)
            return
        except AttributeError:
            pass

        self.no_pixels_button.setChecked(True)
        self.pixel_options_stack.setVisible(False)

    def _fill_single_pixel_fields(self, component_to_edit: Component):
        """
        Fill the "single pixel" fields of a component that's being edited and contains pixel information.
        :param component_to_edit: The component that's being edited.
        """
        # Retrieve the pixel offsets and detector number from the component
        x_pixel_offset = component_to_edit.get_field_value(X_PIXEL_OFFSET)
        y_pixel_offset = component_to_edit.get_field_value(Y_PIXEL_OFFSET)
        detector_numbers = component_to_edit.get_field_value(DETECTOR_NUMBER).tolist()

        # Check that x offset is more than one value
        if data_is_an_array_with_more_than_one_element(x_pixel_offset):

            # Set the number of rows and the row height
            n_rows, row_height = self._get_row_information(y_pixel_offset)
            self.row_count_spin_box.setValue(n_rows)
            self.row_height_spin_box.setValue(row_height)

            # Set the number of columns and the column width
            n_cols, col_width = self._get_column_information(x_pixel_offset)
            self.column_count_spin_box.setValue(n_cols)
            self.column_width_spin_box.setValue(col_width)

            # Set the first ID, start counting option, and the count direction option
            (
                first_id,
                start_counting_text,
                count_along_text,
            ) = self._get_detector_number_information(detector_numbers)
            self.first_id_spin_box.setValue(first_id)
            self.start_counting_combo_box.setCurrentText(start_counting_text)
            self.count_first_combo_box.setCurrentText(count_along_text)

        else:
            # If the pixel offset information represents a single pixel
            pass

    @staticmethod
    def _get_row_information(y_pixel_offset: np.ndarray) -> Tuple[int, Optional[float]]:
        """
        Determine the number of rows and the row height from a component that's being edited.
        :param y_pixel_offset: The array of y pixel offsets from the component.
        :return: The number of rows and the row height. If there is only one row, the row height is treated as None.
        """
        n_rows = y_pixel_offset.shape[0]

        if n_rows > 1:
            return n_rows, np.abs(y_pixel_offset[0][0] - y_pixel_offset[1][0])

        return n_rows, None

    @staticmethod
    def _get_column_information(
        x_pixel_offset: np.ndarray,
    ) -> Tuple[int, Optional[float]]:
        """
        Determine the number of columns and the column width from a component that's being edited.
        :param x_pixel_offset: The array of x pixel offsets from the component.
        :return: The number of columns and the column width. if there is only one column, column width is treated as
        None.
        """
        n_cols = x_pixel_offset.shape[1]

        if n_cols > 1:
            return n_cols, np.abs(x_pixel_offset[0][1] - x_pixel_offset[0][0])

        return n_cols, None

    @staticmethod
    def _get_detector_number_information(
        detector_numbers: List[List[int]],
    ) -> Tuple[int, str, str]:
        """
        Determine the first pixel ID, the count direction, and the location of the first pixel from a component that's
        being edited.
        :param detector_numbers: The array of detector numbers from the component.
        :return: The first ID, start counting text, and count along text that should be placed in the Edit Component
        Window.
        """
        # Find the first pixel and its index in the detector number array
        first_id = np.amin(detector_numbers)
        first_id_index = np.where(detector_numbers == first_id)
        first_id_index = (first_id_index[0][0], first_id_index[1][0])

        # Find the indices that are right and left of the first ID. A pixel will not always exist in these places, so
        # a check is done before accessing the values at these indices.
        right_of_first_id = (first_id_index[0], first_id_index[1] + 1)
        left_of_first_id = (first_id_index[0], first_id_index[1] - 1)

        start_counting = []

        # Use the index from the first pixel to determine if the first ID is at the top or bottom of the grid
        if first_id_index[0] == 0:
            start_counting.append("Top")
        else:
            start_counting.append("Bottom")

        # Set the count along text to columns
        count_along_text = COLUMNS_TEXT

        # Find the value after the first ID
        first_id_plus_one = first_id + 1

        # Determine if the first ID is on the right or left of the pixel grid
        if first_id_index[1] == 0:
            start_counting.append("Left")
            # If the first pixel is on the left of the grid, check if its neighbour on the right is the second pixel
            # If it is the second pixel, the count along value is Rows, otherwise it will remain as Columns
            if (
                detector_numbers[right_of_first_id[0]][right_of_first_id[1]]
                == first_id_plus_one
            ):
                count_along_text = ROWS_TEXT

        else:
            start_counting.append("Right")
            # If the first pixel is on the right of the grid, check if its neighbour on the left is the second pixel
            # If it is the second pixel, the count along value is Rows, otherwise it will remain as columns
            if (
                detector_numbers[left_of_first_id[0]][left_of_first_id[1]]
                == first_id_plus_one
            ):
                count_along_text = ROWS_TEXT

        start_counting_text = " ".join(start_counting)

        return first_id, start_counting_text, count_along_text

    def _fill_entire_shape_fields(self, component_to_edit: Component):
        """
        Fill the "entire shape" fields a component that is being edited and contains pixel data.
        :param component_to_edit: The component being edited.
        """
        shape = component_to_edit.shape[0]

        if isinstance(shape, OFFGeometryNexus):
            self._fill_off_geometry_pixel_mapping(shape)

        elif not isinstance(shape, BoxGeometry):
            detector_number = shape.detector_number
            n_cylinders = shape.cylinders.size // 3

            if n_cylinders > 1:
                self.create_pixel_mapping_table(n_cylinders, "cylinder")
                # TODO: Restore pixel mapping in the case of multiple cylinders

            else:
                self.create_pixel_mapping_table(n_cylinders, "cylinder")
                item = QTableWidgetItem()
                item.setData(Qt.DisplayRole, detector_number[0])
                self.pixel_mapping_table_widget.setItem(0, 1, item)

    def _fill_off_geometry_pixel_mapping(self, shape: OFFGeometryNexus):
        """
        Fill in the pixel mapping information from an OFFGeometry component.
        :param shape: The shape data from the NeXus file.
        """
        # Retrieve the detector face information from the shape and use this to create the required number of pixel
        # mapping widgets
        n_faces, detector_faces = self._get_detector_face_information(shape)
        self.create_pixel_mapping_table(n_faces, "face")

        # Populate the pixel mapping widgets based on the contents of the detector_faces array
        for detector_face in detector_faces:
            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, detector_face[1])
            self.pixel_mapping_table_widget.setItem(
                detector_face[0], 1, QTableWidgetItem(item)
            )

    @staticmethod
    def _get_detector_face_information(
        shape: OFFGeometryNexus,
    ) -> Tuple[int, List[Tuple[int, int]]]:
        return len(shape.faces), shape.detector_faces

    def get_current_mapping_filename(self) -> str:
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
        self.count_first_combo_box.addItems(list(COUNT_DIRECTION.keys()))

    @property
    def validator(self):
        """
        :return: The PixelOptions' PixelValidator. This is needed in the AddComponentDialog so that it has knowledge
        of the PixelOptions' validity status.
        """
        return self._pixel_validator

    def generate_pixel_mapping_if_required(self):
        """
        Informs the AddComponentDialog that the "Entire Shape" button has been pressed. This then causes the
        AddComponentDialog to check if a new and valid file has been given. If these conditions are met then the
        AddComponentDialog will call the method for populating the pixel mapping table. If these conditions are not met
        then the list will remain empty.
        """
        if self.pixel_mapping_table_widget.rowCount() == 0:
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
        self._pixel_validator.set_pixel_grid_valid(
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
            self.pixel_options_stack.setCurrentIndex(PIXEL_GRID_STACK_INDEX)
        elif pixel_mapping:
            self.pixel_options_stack.setCurrentIndex(PIXEL_MAPPING_STACK_INDEX)

    def populate_pixel_mapping_list_with_mesh(self, filename: str):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file for
        an NXoff_geometry.
        """
        if self.pixel_mapping_not_visible():
            return

        n_faces = self.get_number_of_faces_from_mesh_file(filename)

        self.reset_pixel_mapping_table()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        self.create_pixel_mapping_table(n_faces, "face")

        # Record the filename of the current mapping to prevent the widgets from being created twice
        self.current_mapping_filename = filename

    def populate_pixel_mapping_list_with_cylinder_number(self, cylinder_number: int):
        """
        Populates the pixel mapping table based on a number of cylinders for the NXcylindrical_geometry.
        :param cylinder_number: The number of cylinders.
        """
        if self.pixel_mapping_not_visible():
            return

        # Set the mapping filename to None as cylinder mappings are not based on a mesh file.
        self.reset_pixel_mapping_table()
        self.create_pixel_mapping_table(cylinder_number, "cylinder")

    @staticmethod
    def get_number_of_faces_from_mesh_file(filename: str) -> int:
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

    def get_pixel_mapping_ids(self) -> List[int]:
        """
        :return: A list of the IDs for the current PixelMappingWidgets.
        """
        ret_list = []
        for i in range(self.pixel_mapping_table_widget.rowCount()):
            ret_list.append(self.get_id_at_index(i))
        return ret_list

    def update_pixel_mapping_validity(self):
        """
        Checks that at least one ID has been given in the Pixel Mapping and then updates the PixelValidator.
        """
        nonempty_ids = []
        for i in range(self.pixel_mapping_table_widget.rowCount()):
            val = self.get_id_at_index(i)
            nonempty_ids.append(val is not None)
        self._pixel_validator.set_pixel_mapping_valid(any(nonempty_ids))

    def generate_pixel_data(self) -> PixelData:
        """
        Creates the appropriate PixelData object depending on user selection then gives it the information that the
        user entered in the relevant fields. If the "No Pixel" button has been pressed then the method returns None.
        In the case of a PixelGrid where either rows/columns has been set to zero, this also causes the matching
        distance value to be recorded as zero.
        :return: A PixelData object or None.
        """
        if self.single_pixel_radio_button.isChecked():

            return PixelGrid(
                rows=self.row_count_spin_box.value(),
                columns=self.column_count_spin_box.value(),
                row_height=self.row_height_spin_box.value(),
                col_width=self.column_width_spin_box.value(),
                first_id=self.first_id_spin_box.value(),
                count_direction=COUNT_DIRECTION[
                    self.count_first_combo_box.currentText()
                ],
                initial_count_corner=INITIAL_COUNT_CORNER[
                    self.start_counting_combo_box.currentText()
                ],
            )

        if self.entire_shape_radio_button.isChecked():
            return PixelMapping(self.get_pixel_mapping_ids())

        return None

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
            self._pixel_validator.inform_ok_validator()

    def pixel_mapping_not_visible(self) -> bool:
        """
        Checks if the pixel mapping options are visible. This is used to determine if it is necessary to generate a
        pixel mapping table.
        :return: A bool indicating the current index of the PixelOptions stack.
        """
        return self.pixel_options_stack.currentIndex() != PIXEL_MAPPING_STACK_INDEX

    def reset_pixel_mapping_table(self):
        """
        Clear the current pixel mapping table and widget. Used when the mesh file changes in the case of NXoff_geometry,
        when the number of cylinders change in the case of NXcylindrical_geometry, or when the user switches between
        mesh and cylinder.
        """
        self.pixel_mapping_table_widget.clear()
        self.current_mapping_filename = None

    def get_id_at_index(self, index: int):
        table_item = self.pixel_mapping_table_widget.item(index, 1)
        if not table_item or not table_item.text():
            return None
        return int(table_item.text())

    def item_changed(self, Qitem: QTableWidgetItem):
        if not Qitem.text() or Qitem.column() == 0:
            return
        try:
            int(Qitem.text())
        except ValueError:
            Msgbox = QMessageBox()
            Msgbox.setText("Error, Pixel ID must be an integer!")
            Msgbox.exec()
            Qitem.setData(Qt.DisplayRole, None)

    def get_pixel_mapping_table_size(self):
        return self.pixel_mapping_table_widget.rowCount()

    def create_pixel_mapping_table(self, n_items: int, text: str):
        """
        Creates a table of pixel mapping widgets.
        :param n_items: The number of widgets to create.
        :param text: The label to be displayed next to the id cel.
        This is either faces or cylinders.
        """
        self.reset_pixel_mapping_table()
        self.pixel_mapping_table_widget.setColumnCount(2)
        self.pixel_mapping_table_widget.setRowCount(n_items)

        for i in range(n_items):
            col_text = f"Pixel ID for {text} #{i}:"
            item = QTableWidgetItem()
            item.setData(Qt.DisplayRole, col_text)
            self.pixel_mapping_table_widget.setItem(i, 0, item)
        self.pixel_mapping_table_widget.resizeColumnToContents(0)
        self.pixel_mapping_table_widget.itemChanged.connect(
            self.update_pixel_mapping_validity
        )

    pixel_mapping_button_pressed = Signal()
