from PySide2.QtWidgets import QSpinBox, QDoubleSpinBox, QListWidgetItem
from nexusutils.readwriteoff import parse_off_file

from nexus_constructor.component_type import PIXEL_COMPONENT_TYPES
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, CountDirection, Corner
from nexus_constructor.pixel_mapping_widget import PixelMappingWidget

RED_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #f6989d }"
WHITE_BACKGROUND_STYLE_SHEET = "QSpinBox { background-color: #FFFFFF }"


class PixelOptions:
    def __init__(self, add_component_dialog):

        self.dialog = add_component_dialog
        self.pixel_mapping_widgets = []

        # Dictionaries that map user-input to known pixel grid options. Used when created the PixelGridModel.
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

    def setup_ui(self):

        self.dialog.singlePixelRadioButton.clicked.connect(
            lambda: self.update_pixel_layout_validity(True, False)
        )
        self.dialog.entireShapeRadioButton.clicked.connect(
            lambda: self.update_pixel_layout_validity(False, True)
        )
        self.dialog.entireShapeRadioButton.clicked.connect(
            self.populate_pixel_mapping_list
        )
        self.dialog.noPixelsButton.clicked.connect(self.hide_pixel_options_stack)

        self.dialog.rowCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_size_field(
                self.dialog.rowCountSpinBox, self.dialog.rowHeightSpinBox
            )
        )
        self.dialog.rowCountSpinBox.valueChanged.connect(self.check_pixel_grid_validity)
        self.dialog.columnCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_size_field(
                self.dialog.columnCountSpinBox, self.dialog.columnWidthSpinBox
            )
        )

        self.dialog.singlePixelRadioButton.clicked.connect(
            self.evaluate_pixel_input_validity
        )
        self.dialog.entireShapeRadioButton.clicked.connect(
            self.evaluate_pixel_input_validity
        )
        self.dialog.noPixelsButton.clicked.connect(self.evaluate_pixel_input_validity)

        self.dialog.countFirstComboBox.addItems(list(self.count_direction.keys()))

        self.dialog.columnCountSpinBox.valueChanged.connect(
            self.check_pixel_grid_validity
        )

    def disable_or_enable_size_field(
        self, count_spin_box: QSpinBox, size_spin_box: QDoubleSpinBox
    ):
        size_spin_box.setEnabled(count_spin_box.value() != 0)
        self.forbid_both_row_and_columns_being_zero()

    def forbid_both_row_and_columns_being_zero(self):
        """
        Changes the column and row count spin boxes in the Pixel
        """

        if (
            self.dialog.rowCountSpinBox.value() == 0
            and self.dialog.columnCountSpinBox.value() == 0
        ):
            self.dialog.rowCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.dialog.columnCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.dialog.ok_validator.set_pixel_grid_valid(False)
        else:
            self.dialog.rowCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.dialog.columnCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.dialog.ok_validator.set_pixel_grid_valid(True)

    def check_pixel_grid_validity(self):
        """
        Update the OK Validator to reflect the validity of the current Pixel Grid input. A PixelGrid is valid provided
        that the rows or columns have a non-zero value. It is invalid if both are zero. The Spin Boxes enforce
        everything else so this is the only check required.
        """
        self.dialog.ok_validator.set_pixel_grid_valid(
            not (
                self.dialog.rowCountSpinBox.value() == 0
                and self.dialog.columnCountSpinBox.value() == 0
            )
        )

    def update_pixel_layout_validity(self, pixel_grid: bool, pixel_mapping: bool):

        self.dialog.pixelOptionsStack.setVisible(True)

        if pixel_grid:
            self.dialog.pixelOptionsStack.setCurrentIndex(0)
        if pixel_mapping:
            self.dialog.pixelOptionsStack.setCurrentIndex(1)

    def populate_pixel_mapping_list(self):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file.
        """

        n_faces = None

        if (
            self.dialog.cad_file_name is None
            or not self.dialog.valid_file_given
            or self.pixel_mapping_not_visible()
        ):
            return

        with open(self.dialog.cad_file_name) as temp_off_file:
            faces = parse_off_file(temp_off_file)[1]
            n_faces = len(faces)

        # Clear the list widget in case it contains information from a previous file.
        self.pixel_mapping_widgets = []
        self.dialog.pixelMappingListWidget.clear()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        for i in range(n_faces):
            pixel_mapping_widget = PixelMappingWidget(
                self.dialog.pixelMappingListWidget, i
            )
            pixel_mapping_widget.pixelIDLineEdit.textChanged.connect(
                self.check_pixel_mapping_validity
            )

            list_item = QListWidgetItem()
            list_item.setSizeHint(pixel_mapping_widget.sizeHint())

            self.dialog.pixelMappingListWidget.addItem(list_item)
            self.dialog.pixelMappingListWidget.setItemWidget(
                list_item, pixel_mapping_widget
            )

            # Keep the PixelMappingWidget so that its ID can be retrieved easily when making a PixelMapping object.
            self.pixel_mapping_widgets.append(pixel_mapping_widget)

    def get_visibility_conditions(self):
        """
        Determine which of the pixel-related fields need to be visible.
        :return: Booleans indicating whether the pixel layout, pixel grid, and pixel mapping options need to
        be made visible.
        """

        pixel_options_condition = self.dialog.componentTypeComboBox.currentText() in PIXEL_COMPONENT_TYPES and (
            self.dialog.meshRadioButton.isChecked()
            or self.dialog.CylinderRadioButton.isChecked()
        )

        if not pixel_options_condition:
            return False, False, False

        else:
            return (
                True,
                self.dialog.singlePixelRadioButton.isChecked(),
                self.dialog.entireShapeRadioButton.isChecked(),
            )

    def update_visibility(
        self, pixel_options_condition, pixel_grid_condition, pixel_mapping_condition
    ):
        """
        Changes the visibility of the pixel-related fields and the box that contains them. First checks if any of the
        fields need to be shown then uses this to determine if the box is needed. After that the visibility of the box
        and individual fields is set.
        """

        # Only make the pixel box appear based on the pixel layout and pixel data options being visible. The pixel grid
        # and mapping options already depend on pixel layout being visible.
        self.dialog.pixelOptionsBox.setVisible(pixel_options_condition)

        # Set visibility for the components of the pixel options box
        self.update_pixel_layout_validity(pixel_grid_condition, pixel_mapping_condition)

    def update_validity(
        self, pixel_options_condition, pixel_grid_condition, pixel_mapping_condition
    ):
        pass

    def hide_pixel_options_stack(self):
        self.dialog.pixelOptionsStack.setVisible(False)

    def update(self,):

        pixel_options_condition, pixel_grid_condition, pixel_mapping_condition = (
            self.get_visibility_conditions()
        )
        self.update_visibility(
            pixel_options_condition, pixel_grid_condition, pixel_mapping_condition
        )
        self.update_validity(
            pixel_options_condition, pixel_grid_condition, pixel_mapping_condition
        )

    def get_pixel_mapping_ids(self):
        """
        :return: A list of the IDs for the current PixelMappingWidgets.
        """
        return [
            pixel_mapping_widget.get_id()
            for pixel_mapping_widget in self.pixel_mapping_widgets
        ]

    def check_pixel_mapping_validity(self):

        nonempty_ids = [
            widget.get_id() is not None for widget in self.pixel_mapping_widgets
        ]
        self.dialog.ok_validator.set_pixel_mapping_valid(any(nonempty_ids))

    def generate_pixel_data(self):
        """
        Creates the appropriate PixelModel object depending on user selection then gives it the information that the
        user entered in the relevant fields.
        :return:
        """
        # Determine which type of PixelMapping object ought to be created.
        _, pixel_grid_condition, pixel_mapping_condition = (
            self.get_visibility_conditions()
        )

        if pixel_grid_condition:
            pixel_data = PixelGrid()
            pixel_data.rows = self.dialog.rowCountSpinBox.value()
            pixel_data.columns = self.dialog.columnCountSpinBox.value()
            pixel_data.row_height = self.dialog.rowHeightSpinBox.value()
            pixel_data.column_width = self.dialog.columnWidthLineEdit.value()
            pixel_data.first_id = self.dialog.firstIDSpinBox.value()
            pixel_data.count_direction = self.dialog.count_direction[
                self.dialog.countFirstComboBox.currentText()
            ]

            pixel_data.initial_count_corner = self.initial_count_corner[
                self.dialog.startCountingComboBox.currentText()
            ]

            return pixel_data

        elif pixel_mapping_condition:
            return PixelMapping(self.get_pixel_mapping_ids())

        else:
            return None

    def evaluate_pixel_input_validity(self):
        """
        Changes the state of the OK Validator depending on whether or not the pixel input is valid. If The No Pixel
        option has been selected then there is nothing to do outside of calling `validate_ok` again.
        """

        if self.dialog.singlePixelRadioButton.isChecked():
            self.check_pixel_grid_validity()
        elif self.dialog.entireShapeRadioButton.isChecked():
            self.check_pixel_mapping_validity()
        else:
            self.dialog.ok_validator.validate_ok()

    def pixel_mapping_not_visible(self):

        return (
            not self.dialog.pixelOptionsStack.isVisible()
            or self.dialog.pixelOptionsStack.currentIndex() == 0
        )
