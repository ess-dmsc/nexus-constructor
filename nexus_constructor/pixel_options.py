from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import QSpinBox, QDoubleSpinBox, QListWidgetItem

from nexus_constructor.geometry.geometry_loader import load_geometry
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, CountDirection, Corner
from nexus_constructor.pixel_mapping_widget import PixelMappingWidget
from nexus_constructor.validators import PixelValidator
from ui.pixel_options import Ui_PixelOptionsWidget

RED_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #f6989d }"
WHITE_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #FFFFFF }"


class PixelOptions(Ui_PixelOptionsWidget, QObject):
    def __init__(self):

        QObject.__init__(self)

        self.pixel_mapping_widgets = []

        # Dictionaries that map user-input to known pixel grid options. Used when creatimg the PixelGrid.
        self.count_direction = {
            "Rows": CountDirection.ROW,
            "Columns": CountDirection.COLUMN,
        }
        self.initial_count_corner = {
            "Bottom Left": Corner.BOTTOM_LEFT,
            "Bottom Right": Corner.BOTTOM_RIGHT,
            "Top Left": Corner.TOP_LEFT,
            "Top Right": Corner.TOP_RIGHT,
        }

        self.pixel_validator = None
        self.current_mapping_filename = None

    def setupUi(self, parent_widget):

        super().setupUi(parent_widget)

        self.pixel_validator = PixelValidator(
            parent_widget, self.singlePixelRadioButton, self.entireShapeRadioButton
        )

        # Have the radio buttons change the visibility of the pixel options
        self.setup_visibility_signals()

        # Have the pixel mapping button populate the list widget if necessary
        self.entireShapeRadioButton.clicked.connect(
            self.generate_pixel_mapping_if_required
        )

        # Setup the pixel grid behaviour
        self.setup_pixel_grid_options()

        # Cause the overall Pixel Options validity to change when a different type of Pixel Layout has been selected
        self.singlePixelRadioButton.clicked.connect(self.evaluate_pixel_input_validity)
        self.entireShapeRadioButton.clicked.connect(self.evaluate_pixel_input_validity)
        self.noPixelsButton.clicked.connect(self.evaluate_pixel_input_validity)

        # Update the validity
        self.evaluate_pixel_input_validity()

    def fill_existing_entries(self):
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
        self.singlePixelRadioButton.clicked.connect(
            lambda: self.update_pixel_layout_visibility(True, False)
        )
        self.entireShapeRadioButton.clicked.connect(
            lambda: self.update_pixel_layout_visibility(False, True)
        )
        self.noPixelsButton.clicked.connect(self.hide_pixel_options_stack)

    def setup_pixel_grid_options(self):
        """
        Deals with connecting the pixel grid's signals to methods that check for validity or enforce certain rules about
        the input.
        """

        # Make the column and row count spin boxes in the Pixel Grid trigger a validity update
        self.rowCountSpinBox.valueChanged.connect(self.update_pixel_grid_validity)
        self.columnCountSpinBox.valueChanged.connect(self.update_pixel_grid_validity)
        # Make the row/column count being set to zero cause its matching distance field to become disabled
        self.columnCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_distance_field(
                self.columnCountSpinBox, self.columnWidthSpinBox
            )
        )
        self.rowCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_distance_field(
                self.rowCountSpinBox, self.rowHeightSpinBox
            )
        )
        # Prevent both the rows and columns in the PixelGrid from being zero
        self.columnCountSpinBox.valueChanged.connect(
            self.forbid_both_row_and_columns_being_zero
        )
        self.rowCountSpinBox.valueChanged.connect(
            self.forbid_both_row_and_columns_being_zero
        )

        # Manually add options to the "Count first along" combo box. This is done here because inserting these options
        # through Qt Designer doesn't work.
        self.countFirstComboBox.addItems(list(self.count_direction.keys()))

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
        if self.pixelMappingListWidget.count() == 0:
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

    def forbid_both_row_and_columns_being_zero(self):
        """
        Changes the StyleSheet of the column and row count spin boxes in the Pixel Grid depending on their validity.
        Sets them to red if both are zero, white if one or neither of them are zero.
        """
        if self.rowCountSpinBox.value() == 0 and self.columnCountSpinBox.value() == 0:
            self.rowCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.columnCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
        else:
            self.rowCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.columnCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)

    def update_pixel_grid_validity(self):
        """
        Update the OK Validator to reflect the validity of the current Pixel Grid input. A PixelGrid is valid provided
        that the rows or columns have a non-zero value. It is invalid if both are zero. The Spin Boxes enforce
        everything else so this is the only check required.
        """
        self.pixel_validator.set_pixel_grid_valid(
            not (
                self.rowCountSpinBox.value() == 0
                and self.columnCountSpinBox.value() == 0
            )
        )

    def update_pixel_layout_visibility(self, pixel_grid: bool, pixel_mapping: bool):
        """
        Changes the visibility of the Pixel Options stack. This displays either the Pixel Grid or the Pixel Mapping.
        :param pixel_grid: Bool indicating whether or not to show the pixel grid options.
        :param pixel_mapping: Bool indicating whether or not to show the pixel mapping options.
        """
        self.pixelOptionsStack.setVisible(True)

        if pixel_grid:
            self.pixelOptionsStack.setCurrentIndex(0)
        if pixel_mapping:
            self.pixelOptionsStack.setCurrentIndex(1)

    def populate_pixel_mapping_list_with_mesh(self, filename: str):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file.
        :return A bool indicating whether or not the pixel mapping widgets have been created.
        """
        if self.pixel_mapping_not_visible():
            return

        n_faces = self.get_number_of_faces_from_mesh_file(filename)

        self.reset_pixel_mapping_list()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        self.create_pixel_mapping_list(n_faces, "faces")

        self.current_mapping_filename = filename

    def populate_pixel_mapping_list_with_cylinder_number(self, cylinder_number: int):

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
        self.pixelOptionsStack.setVisible(False)

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
        if self.singlePixelRadioButton.isChecked():

            rows = self.rowCountSpinBox.value()
            row_height = self.rowHeightSpinBox.value()

            if rows == 0:
                row_height = 0

            columns = self.columnCountSpinBox.value()
            col_width = self.columnWidthSpinBox.value()

            if columns == 0:
                col_width = 0

            return PixelGrid(
                rows=rows,
                columns=columns,
                row_height=row_height,
                col_width=col_width,
                first_id=self.firstIDSpinBox.value(),
                count_direction=self.count_direction[
                    self.countFirstComboBox.currentText()
                ],
                initial_count_corner=self.initial_count_corner[
                    self.startCountingComboBox.currentText()
                ],
            )

        if self.entireShapeRadioButton.isChecked():
            return PixelMapping(self.get_pixel_mapping_ids())

        if self.noPixelsButton.isChecked():
            return None

    def evaluate_pixel_input_validity(self):
        """
        Changes the state of the OK Validator depending on whether or not the pixel input is valid. If The No Pixel
        option has been selected then there is nothing to do outside of calling `validate_pixels` again.
        """

        if self.singlePixelRadioButton.isChecked():
            self.update_pixel_grid_validity()
        elif self.entireShapeRadioButton.isChecked():
            self.update_pixel_mapping_validity()
        else:
            self.pixel_validator.inform_ok_validator()

    def pixel_mapping_not_visible(self):
        """
        Checks if the pixel mapping options are visible. This is used to determine if it is necessary to generate a
        pixel mapping list.
        :return: A bool indicating the current index of the PixelOptions stack.
        """
        return self.pixelOptionsStack.currentIndex() != 1

    def reset_pixel_mapping_list(self):

        # Clear the list widget in case it contains information from a previous file.
        self.pixel_mapping_widgets = []
        self.pixelMappingListWidget.clear()

    def create_pixel_mapping_list(self, n_items, text):

        for i in range(n_items):
            pixel_mapping_widget = PixelMappingWidget(
                self.pixelMappingListWidget, i, text
            )
            pixel_mapping_widget.pixelIDLineEdit.textChanged.connect(
                self.update_pixel_mapping_validity
            )

            # Make sure the list item is as large as the widget
            list_item = QListWidgetItem()
            list_item.setSizeHint(pixel_mapping_widget.sizeHint())

            self.pixelMappingListWidget.addItem(list_item)
            self.pixelMappingListWidget.setItemWidget(list_item, pixel_mapping_widget)

            # Keep the PixelMappingWidget so that its ID can be retrieved easily when making a PixelMapping object.
            self.pixel_mapping_widgets.append(pixel_mapping_widget)

    pixel_mapping_button_pressed = Signal()
