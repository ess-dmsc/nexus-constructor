from PySide2 import QtCore, QtWidgets


class Ui_Link(object):
    def setupUi(self, Link):
        Link.resize(406, 96)
        self.main_layout = QtWidgets.QVBoxLayout(Link)
        self.group_box = QtWidgets.QGroupBox(Link)
        self.group_box.setObjectName("groupBox")
        self.vertical_layout = QtWidgets.QVBoxLayout(self.group_box)
        self.select_link_label = QtWidgets.QLabel(self.group_box)
        self.vertical_layout.addWidget(self.select_link_label)
        self.transformations_combo_box = QtWidgets.QComboBox(self.group_box)
        self.vertical_layout.addWidget(self.transformations_combo_box)
        self.group_box.setLayout(self.vertical_layout)
        self.main_layout.addWidget(self.group_box)

        self.retranslateUi(Link)
        QtCore.QMetaObject.connectSlotsByName(Link)

    def retranslateUi(self, Link):
        Link.setWindowTitle(QtWidgets.QApplication.translate("Link", "Frame", None, -1))
        self.group_box.setTitle(
            QtWidgets.QApplication.translate("Link", "Link", None, -1)
        )
        self.select_link_label.setText(
            QtWidgets.QApplication.translate("Link", "Select component", None, -1)
        )
