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
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.transformations_combo_box = QtWidgets.QComboBox(self.group_box)
        combo_size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        combo_size_policy.setHorizontalStretch(1)
        combo_size_policy.setVerticalStretch(0)
        self.transformations_combo_box.setSizePolicy(combo_size_policy)
        self.horizontal_layout.addWidget(self.transformations_combo_box)
        self.go_to_link = QtWidgets.QPushButton("Go to", self.group_box)
        self.go_to_link.setEnabled(False)
        self.transformations_combo_box.currentIndexChanged.connect(self.setLinkEvent)
        self.horizontal_layout.addWidget(self.go_to_link)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.group_box.setLayout(self.vertical_layout)
        self.main_layout.addWidget(self.group_box)

        self.retranslateUi(Link)
        QtCore.QMetaObject.connectSlotsByName(Link)

    def setLinkEvent(self, new_index):
        self.go_to_link.setEnabled(new_index > 0)

    def retranslateUi(self, Link):
        Link.setWindowTitle(QtWidgets.QApplication.translate("Link", "Frame", None, -1))
        self.group_box.setTitle(
            QtWidgets.QApplication.translate("Link", "Link", None, -1)
        )
        self.select_link_label.setText(
            QtWidgets.QApplication.translate("Link", "Select component", None, -1)
        )
