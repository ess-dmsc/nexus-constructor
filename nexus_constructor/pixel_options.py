from PySide2.QtCore import Signal, QObject
from PySide2.QtWidgets import QSpinBox, QDoubleSpinBox, QListWidgetItem
from nexusutils.readwriteoff import parse_off_file

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

    def setupUi(self, parent_widget):

        super().setupUi(parent_widget)

        self.pixel_validator = PixelValidator(
            parent_widget, self.singlePixelRadioButton, self.entireShapeRadioButton
        )

        self.singlePixelRadioButton.clicked.connect(
            lambda: self.update_pixel_layout_visibility(True, False)
        )
        self.entireShapeRadioButton.clicked.connect(
            lambda: self.update_pixel_layout_visibility(False, True)
        )
        self.entireShapeRadioButton.clicked.connect(
            self.generate_pixel_mapping_if_empty
        )
        self.noPixelsButton.clicked.connect(self.hide_pixel_options_stack)

        self.rowCountSpinBox.valueChanged.connect(self.check_pixel_grid_validity)
        self.columnCountSpinBox.valueChanged.connect(self.check_pixel_grid_validity)

        self.columnCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_size_field(
                self.columnCountSpinBox, self.columnWidthSpinBox
            )
        )
        self.rowCountSpinBox.valueChanged.connect(
            lambda: self.disable_or_enable_size_field(
                self.rowCountSpinBox, self.rowHeightSpinBox
            )
        )

        self.singlePixelRadioButton.clicked.connect(self.evaluate_pixel_input_validity)
        self.entireShapeRadioButton.clicked.connect(self.evaluate_pixel_input_validity)
        self.noPixelsButton.clicked.connect(self.evaluate_pixel_input_validity)

        self.countFirstComboBox.addItems(list(self.count_direction.keys()))

        self.evaluate_pixel_input_validity()

    def get_validator(self):
        return self.pixel_validator

    def generate_pixel_mapping_if_empty(self):
        self.pixel_mapping_button_pressed.emit()

    def disable_or_enable_size_field(
        self, count_spin_box: QSpinBox, size_spin_box: QDoubleSpinBox
    ):
        size_spin_box.setEnabled(count_spin_box.value() != 0)
        self.forbid_both_row_and_columns_being_zero()

    def forbid_both_row_and_columns_being_zero(self):
        """
        Changes the column and row count spin boxes in the Pixel
        """

        if self.rowCountSpinBox.value() == 0 and self.columnCountSpinBox.value() == 0:
            self.rowCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.columnCountSpinBox.setStyleSheet(RED_BACKGROUND_STYLE_SHEET)
            self.pixel_validator.set_pixel_grid_valid(False)
        else:
            self.rowCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.columnCountSpinBox.setStyleSheet(WHITE_BACKGROUND_STYLE_SHEET)
            self.pixel_validator.set_pixel_grid_valid(True)

    def check_pixel_grid_validity(self):
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

        self.pixelOptionsStack.setVisible(True)

        if pixel_grid:
            self.pixelOptionsStack.setCurrentIndex(0)
        if pixel_mapping:
            self.pixelOptionsStack.setCurrentIndex(1)

    def populate_pixel_mapping_list(self, filename):
        """
        Populates the Pixel Mapping list with widgets depending on the number of faces in the current geometry file.
        """

        n_faces = None

        if self.pixel_mapping_not_visible():
            return

        with open(filename) as temp_off_file:
            faces = parse_off_file(temp_off_file)[1]
            n_faces = len(faces)

        # Clear the list widget in case it contains information from a previous file.
        self.pixel_mapping_widgets = []
        self.pixelMappingListWidget.clear()

        # Use the faces information from the geometry file to add fields to the pixel mapping list
        for i in range(n_faces):
            pixel_mapping_widget = PixelMappingWidget(self.pixelMappingListWidget, i)
            pixel_mapping_widget.pixelIDLineEdit.textChanged.connect(
                self.check_pixel_mapping_validity
            )

            list_item = QListWidgetItem()
            list_item.setSizeHint(pixel_mapping_widget.sizeHint())

            self.pixelMappingListWidget.addItem(list_item)
            self.pixelMappingListWidget.setItemWidget(list_item, pixel_mapping_widget)

            # Keep the PixelMappingWidget so that its ID can be retrieved easily when making a PixelMapping object.
            self.pixel_mapping_widgets.append(pixel_mapping_widget)

    def hide_pixel_options_stack(self):
        self.pixelOptionsStack.setVisible(False)

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
        self.pixel_validator.set_pixel_mapping_valid(any(nonempty_ids))

    def generate_pixel_data(self):
        """
        Creates the appropriate PixelModel object depending on user selection then gives it the information that the
        user entered in the relevant fields.
        :return:
        """

        if self.pixelOptionsStack.currentIndex() == 0:
            pixel_data = PixelGrid()
            pixel_data.rows = self.rowCountSpinBox.value()
            pixel_data.columns = self.columnCountSpinBox.value()
            pixel_data.row_height = self.rowHeightSpinBox.value()
            pixel_data.column_width = self.columnWidthSpinBox.value()
            pixel_data.first_id = self.firstIDSpinBox.value()
            pixel_data.count_direction = self.count_direction[
                self.countFirstComboBox.currentText()
            ]

            pixel_data.initial_count_corner = self.initial_count_corner[
                self.startCountingComboBox.currentText()
            ]

            return pixel_data

        else:
            return PixelMapping(self.get_pixel_mapping_ids())

    def evaluate_pixel_input_validity(self):
        """
        Changes the state of the OK Validator depending on whether or not the pixel input is valid. If The No Pixel
        option has been selected then there is nothing to do outside of calling `validate_pixels` again.
        """

        if self.singlePixelRadioButton.isChecked():
            self.check_pixel_grid_validity()
        elif self.entireShapeRadioButton.isChecked():
            self.check_pixel_mapping_validity()
        else:
            self.pixel_validator.validate_pixels()

    def pixel_mapping_not_visible(self):

        return (
            not self.pixelOptionsStack.isVisible()
            or self.pixelOptionsStack.currentIndex() == 0
        )

    pixel_mapping_button_pressed = Signal()
