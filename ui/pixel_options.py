# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/pixel_options.ui',
# licensing of 'ui/pixel_options.ui' applies.
#
# Created: Wed Aug 14 09:30:56 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtWidgets


class Ui_PixelOptionsWidget(object):
    def setupUi(self, PixelOptionsWidget):
        PixelOptionsWidget.setObjectName("PixelOptionsWidget")
        PixelOptionsWidget.resize(560, 403)

        PixelOptionsWidget.setMinimumSize(QtCore.QSize(560, 20))
        self.main_layout = QtWidgets.QVBoxLayout(PixelOptionsWidget)
        self.main_layout.setObjectName("verticalLayout_2")
        self.pixel_options_group_box = QtWidgets.QGroupBox(PixelOptionsWidget)

        self.pixel_options_group_box.setMinimumSize(QtCore.QSize(0, 20))
        self.pixel_options_group_box.setObjectName("pixelOptionsBox")
        self.group_box_layout = QtWidgets.QVBoxLayout(self.pixel_options_group_box)
        self.group_box_layout.setObjectName("verticalLayout_3")
        self.pixel_layout_group_box = QtWidgets.QGroupBox(self.pixel_options_group_box)
        self.pixel_layout_group_box.setMinimumSize(QtCore.QSize(0, 63))
        self.pixel_layout_group_box.setObjectName("pixelLayoutBox")
        self.pixel_layout_group_box_layout = QtWidgets.QHBoxLayout(
            self.pixel_layout_group_box
        )
        self.pixel_layout_group_box_layout.setObjectName("horizontalLayout_7")
        self._set_up_radio_buttons()
        self.group_box_layout.addWidget(self.pixel_layout_group_box)

        self._set_up_pixel_options_stack()

        self._set_up_pixel_mapping()

        self.group_box_layout.addWidget(self.pixel_options_stack)
        self.main_layout.addWidget(self.pixel_options_group_box)

        self.retranslateUi(PixelOptionsWidget)
        self.pixel_options_stack.setCurrentIndex(0)
        self.count_first_combo_box.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(PixelOptionsWidget)

    def _set_up_radio_buttons(self):
        self.single_pixel_radio_button = QtWidgets.QRadioButton(
            self.pixel_layout_group_box
        )
        self.single_pixel_radio_button.setChecked(True)
        self.single_pixel_radio_button.setObjectName("singlePixelRadioButton")
        self.pixel_layout_group_box_layout.addWidget(self.single_pixel_radio_button)
        self.entire_shape_radio_button = QtWidgets.QRadioButton(
            self.pixel_layout_group_box
        )
        self.entire_shape_radio_button.setObjectName("entireShapeRadioButton")
        self.pixel_layout_group_box_layout.addWidget(self.entire_shape_radio_button)
        self.no_pixels_button = QtWidgets.QRadioButton(self.pixel_layout_group_box)
        self.no_pixels_button.setObjectName("noPixelsButton")
        self.pixel_layout_group_box_layout.addWidget(self.no_pixels_button)

    def _set_up_pixel_mapping(self):
        self.pixel_mapping_page = QtWidgets.QWidget()
        self.pixel_mapping_page.setObjectName("pixelMappingPage")
        self.pixel_mapping_page_layout = QtWidgets.QVBoxLayout(self.pixel_mapping_page)
        self.pixel_mapping_page_layout.setObjectName("verticalLayout_4")
        self.pixel_mapping_label = QtWidgets.QLabel(self.pixel_mapping_page)
        self.pixel_mapping_label.setObjectName("pixelMappingLabel")
        self.pixel_mapping_page_layout.addWidget(self.pixel_mapping_label)
        self.pixel_mapping_table_widget = QtWidgets.QTableWidget(
            self.pixel_mapping_page
        )
        self.pixel_mapping_table_widget.setObjectName("pixelMappingListWidget")
        self.pixel_mapping_page_layout.addWidget(self.pixel_mapping_table_widget)
        self.pixel_options_stack.addWidget(self.pixel_mapping_page)

    def _set_up_pixel_options_stack(self):
        self.pixel_options_stack = QtWidgets.QStackedWidget(
            self.pixel_options_group_box
        )
        self.pixel_options_stack.setMinimumSize(QtCore.QSize(518, 192))
        self.pixel_options_stack.setObjectName("pixelOptionsStack")
        self.pixel_grid_page = QtWidgets.QWidget()
        self.pixel_grid_page.setObjectName("pixelGridPage")
        self.pixel_grid_page_layout = QtWidgets.QVBoxLayout(self.pixel_grid_page)
        self.pixel_grid_page_layout.setObjectName("verticalLayout")
        self._set_up_pixel_grid_group_box()
        self.pixel_options_stack.addWidget(self.pixel_grid_page)

    def _set_up_pixel_grid_group_box(self):
        self.pixel_grid_group_box = QtWidgets.QGroupBox(self.pixel_grid_page)
        self.pixel_grid_group_box.setObjectName("pixelGridBox")
        self.pixel_grid_group_box_layout = QtWidgets.QGridLayout(
            self.pixel_grid_group_box
        )
        self.pixel_grid_group_box_layout.setVerticalSpacing(6)
        self.pixel_grid_group_box_layout.setObjectName("gridLayout_5")
        self.row_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.row_label.setObjectName("rowLabel")
        self.pixel_grid_group_box_layout.addWidget(self.row_label, 0, 0, 1, 1)
        self.row_height_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.row_height_label.setObjectName("rowHeightLabel")
        self.pixel_grid_group_box_layout.addWidget(self.row_height_label, 0, 2, 1, 1)
        self.column_width_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.column_width_label.setObjectName("columnWidthLabel")
        self.pixel_grid_group_box_layout.addWidget(self.column_width_label, 1, 2, 1, 1)
        self.first_id_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.first_id_label.setObjectName("firstIDLabel")
        self.pixel_grid_group_box_layout.addWidget(self.first_id_label, 2, 0, 1, 1)
        self.columns_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.columns_label.setObjectName("columnsLabel")
        self.pixel_grid_group_box_layout.addWidget(self.columns_label, 1, 0, 1, 1)
        self.count_first_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.count_first_label.setObjectName("countFirstLabel")
        self.pixel_grid_group_box_layout.addWidget(self.count_first_label, 4, 0, 1, 2)
        self.counting_from_label = QtWidgets.QLabel(self.pixel_grid_group_box)
        self.counting_from_label.setObjectName("countingFromLabel")
        self.pixel_grid_group_box_layout.addWidget(self.counting_from_label, 3, 0, 1, 2)
        self.start_counting_combo_box = QtWidgets.QComboBox(self.pixel_grid_group_box)
        self.start_counting_combo_box.setMaxCount(4)
        self.start_counting_combo_box.setInsertPolicy(
            QtWidgets.QComboBox.InsertAtCurrent
        )

        self.start_counting_combo_box.setObjectName("startCountingComboBox")
        self.start_counting_combo_box.addItem("")
        self.start_counting_combo_box.addItem("")
        self.start_counting_combo_box.addItem("")
        self.start_counting_combo_box.addItem("")
        self.pixel_grid_group_box_layout.addWidget(
            self.start_counting_combo_box, 3, 2, 1, 2
        )

        self.count_first_combo_box = QtWidgets.QComboBox(self.pixel_grid_group_box)
        self.count_first_combo_box.setCurrentText("")
        self.count_first_combo_box.setMaxCount(2)
        self.count_first_combo_box.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        self.count_first_combo_box.setObjectName("countFirstComboBox")
        self.pixel_grid_group_box_layout.addWidget(
            self.count_first_combo_box, 4, 2, 1, 2
        )

        self.row_count_spin_box = QtWidgets.QSpinBox(self.pixel_grid_group_box)
        self.row_count_spin_box.setMinimum(1)
        self.row_count_spin_box.setMaximum(1000000)
        self.row_count_spin_box.setProperty("value", 1)
        self.row_count_spin_box.setObjectName("rowCountSpinBox")
        self.pixel_grid_group_box_layout.addWidget(self.row_count_spin_box, 0, 1, 1, 1)
        self.column_count_spin_box = QtWidgets.QSpinBox(self.pixel_grid_group_box)
        self.column_count_spin_box.setMinimum(1)
        self.column_count_spin_box.setMaximum(1000000)
        self.column_count_spin_box.setProperty("value", 1)
        self.column_count_spin_box.setObjectName("columnCountSpinBox")
        self.pixel_grid_group_box_layout.addWidget(
            self.column_count_spin_box, 1, 1, 1, 1
        )

        self.first_id_spin_box = QtWidgets.QSpinBox(self.pixel_grid_group_box)
        self.first_id_spin_box.setMaximum(1000000)
        self.first_id_spin_box.setObjectName("firstIDSpinBox")
        self.pixel_grid_group_box_layout.addWidget(self.first_id_spin_box, 2, 1, 1, 1)
        self.row_height_spin_box = QtWidgets.QDoubleSpinBox(self.pixel_grid_group_box)
        self.row_height_spin_box.setMinimum(0.1)
        self.row_height_spin_box.setSingleStep(0.1)
        self.row_height_spin_box.setProperty("value", 0.5)
        self.row_height_spin_box.setObjectName("rowHeightSpinBox")
        self.row_height_spin_box.setMaximum(1000000)
        self.pixel_grid_group_box_layout.addWidget(self.row_height_spin_box, 0, 3, 1, 1)
        self.column_width_spin_box = QtWidgets.QDoubleSpinBox(self.pixel_grid_group_box)
        self.column_width_spin_box.setMinimum(0.1)
        self.column_width_spin_box.setSingleStep(0.1)
        self.column_width_spin_box.setProperty("value", 0.5)
        self.column_width_spin_box.setObjectName("columnWidthSpinBox")
        self.column_width_spin_box.setMaximum(1000000)
        self.pixel_grid_group_box_layout.addWidget(
            self.column_width_spin_box, 1, 3, 1, 1
        )
        self.pixel_grid_page_layout.addWidget(self.pixel_grid_group_box)

    def retranslateUi(self, PixelOptionsWidget):
        PixelOptionsWidget.setWindowTitle(
            QtWidgets.QApplication.translate("PixelOptionsWidget", "Form", None, -1)
        )
        self.pixel_options_group_box.setTitle(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel options", None, -1
            )
        )
        self.pixel_layout_group_box.setTitle(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel layout:", None, -1
            )
        )
        self.single_pixel_radio_button.setToolTip(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget",
                "The defined cylinder or mesh shape describes each identical pixel in the detector",
                None,
                -1,
            )
        )
        self.single_pixel_radio_button.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Repeated Single Pixel Shape", None, -1
            )
        )
        self.entire_shape_radio_button.setToolTip(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget",
                "The defined cylinder or mesh shape describes the shape of the entire detector",
                None,
                -1,
            )
        )
        self.entire_shape_radio_button.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Entire Shape", None, -1
            )
        )
        self.no_pixels_button.setToolTip(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget",
                "The defined cylinder or mesh shape does not define the shape of the detector pixels",
                None,
                -1,
            )
        )
        self.no_pixels_button.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "No Pixels", None, -1
            )
        )
        self.pixel_grid_group_box.setTitle(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel grid:", None, -1
            )
        )
        self.row_label.setText(
            QtWidgets.QApplication.translate("PixelOptionsWidget", "Row:", None, -1)
        )
        self.row_height_label.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Row height:", None, -1
            )
        )
        self.column_width_label.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Column width:", None, -1
            )
        )
        self.first_id_label.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "First ID:", None, -1
            )
        )
        self.columns_label.setText(
            QtWidgets.QApplication.translate("PixelOptionsWidget", "Columns:", None, -1)
        )
        self.count_first_label.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Count first along:", None, -1
            )
        )
        self.counting_from_label.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Start counting from:", None, -1
            )
        )
        self.start_counting_combo_box.setItemText(
            0,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Bottom Left", None, -1
            ),
        )
        self.start_counting_combo_box.setItemText(
            1,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Bottom Right", None, -1
            ),
        )
        self.start_counting_combo_box.setItemText(
            2,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Top Left", None, -1
            ),
        )
        self.start_counting_combo_box.setItemText(
            3,
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Top Right", None, -1
            ),
        )
        self.pixel_mapping_label.setText(
            QtWidgets.QApplication.translate(
                "PixelOptionsWidget", "Pixel mapping:", None, -1
            )
        )
