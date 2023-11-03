from PySide6.QtGui import QVector3D
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QLabel, QPushButton, QSizePolicy, QWidget

from nexus_constructor.instrument_view.instrument_view import InstrumentView


class CameraSettingsTab(QWidget):
    def __init__(self, scene_widget: InstrumentView, parent=None):
        super().__init__()

        self.setParent(parent)
        fix_vertical_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(fix_vertical_size)
        self.cameraSettingsLayout = QGridLayout()

        self.sceneWidget = scene_widget

        self.positionVector_label = QLabel("Camera position")
        self.positionVector_x_dsb = QDoubleSpinBox()
        self.positionVector_y_dsb = QDoubleSpinBox()
        self.positionVector_z_dsb = QDoubleSpinBox()
        self.positionVector_x_dsb.setMinimum(-2000)
        self.positionVector_y_dsb.setMinimum(-2000)
        self.positionVector_z_dsb.setMinimum(-2000)
        self.positionVector_x_dsb.setMaximum(2000)
        self.positionVector_y_dsb.setMaximum(2000)
        self.positionVector_z_dsb.setMaximum(2000)

        self.viewCenterVector_label = QLabel("View center")
        self.viewCenterVector_x_dsb = QDoubleSpinBox()
        self.viewCenterVector_y_dsb = QDoubleSpinBox()
        self.viewCenterVector_z_dsb = QDoubleSpinBox()
        self.viewCenterVector_x_dsb.setMinimum(-2000)
        self.viewCenterVector_y_dsb.setMinimum(-2000)
        self.viewCenterVector_z_dsb.setMinimum(-2000)
        self.viewCenterVector_x_dsb.setMaximum(2000)
        self.viewCenterVector_y_dsb.setMaximum(2000)
        self.viewCenterVector_z_dsb.setMaximum(2000)

        self.fieldOfView_label = QLabel("Field of view")
        self.fieldOfView_dsb = QDoubleSpinBox()

        self.nearField_label = QLabel("Near field")
        self.nearField_dsb = QDoubleSpinBox()
        self.nearField_dsb.setMinimum(0.0001)

        self.farField_label = QLabel("Far field")
        self.farField_dsb = QDoubleSpinBox()
        self.farField_dsb.setMaximum(1500)

        self.aspectRatio_label = QLabel("Aspect ratio")
        self.aspectRatio_1_dsb = QDoubleSpinBox()
        self.aspectRatio_2_dsb = QDoubleSpinBox()

        self.cameraSpeed_label = QLabel("Camera speed")
        self.cameraSpeed_dsb = QDoubleSpinBox()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.update_current_values)

        self.default_btn = QPushButton("Default")
        self.default_btn.clicked.connect(self.set_default_settings)

        self.sideview_btn = QPushButton("Side view")
        self.sideview_btn.clicked.connect(self.switch_to_sideview)

        self.topview_btn = QPushButton("Top view")
        self.topview_btn.clicked.connect(self.switch_to_topview)

        self.frontview_btn = QPushButton("Front view")
        self.frontview_btn.clicked.connect(self.switch_to_frontview)

        self.cameraSettingsLayout.addWidget(self.positionVector_label, 0, 0)
        self.cameraSettingsLayout.addWidget(self.positionVector_x_dsb, 0, 1)
        self.cameraSettingsLayout.addWidget(self.positionVector_y_dsb, 0, 2)
        self.cameraSettingsLayout.addWidget(self.positionVector_z_dsb, 0, 3)

        self.cameraSettingsLayout.addWidget(self.viewCenterVector_label, 1, 0)
        self.cameraSettingsLayout.addWidget(self.viewCenterVector_x_dsb, 1, 1)
        self.cameraSettingsLayout.addWidget(self.viewCenterVector_y_dsb, 1, 2)
        self.cameraSettingsLayout.addWidget(self.viewCenterVector_z_dsb, 1, 3)

        self.cameraSettingsLayout.addWidget(self.fieldOfView_label, 2, 0)
        self.cameraSettingsLayout.addWidget(self.fieldOfView_dsb, 2, 1)

        self.cameraSettingsLayout.addWidget(self.nearField_label, 3, 0)
        self.cameraSettingsLayout.addWidget(self.nearField_dsb, 3, 1)

        self.cameraSettingsLayout.addWidget(self.farField_label, 4, 0)
        self.cameraSettingsLayout.addWidget(self.farField_dsb, 4, 1)

        self.cameraSettingsLayout.addWidget(self.aspectRatio_label, 5, 0)
        self.cameraSettingsLayout.addWidget(self.aspectRatio_1_dsb, 5, 1)
        self.cameraSettingsLayout.addWidget(self.aspectRatio_2_dsb, 5, 2)

        self.cameraSettingsLayout.addWidget(self.cameraSpeed_label, 6, 0)
        self.cameraSettingsLayout.addWidget(self.cameraSpeed_dsb, 6, 1)

        self.cameraSettingsLayout.addWidget(self.sideview_btn, 7, 0)
        self.cameraSettingsLayout.addWidget(self.topview_btn, 7, 1)
        self.cameraSettingsLayout.addWidget(self.frontview_btn, 7, 2)

        self.cameraSettingsLayout.addWidget(self.default_btn, 8, 2)
        self.cameraSettingsLayout.addWidget(self.apply_btn, 8, 3)

        self.initialize_default_values()

        self.sceneWidget.camera_entity.viewCenterChanged.connect(
            self.read_current_values
        )
        self.sceneWidget.camera_entity.positionChanged.connect(self.read_current_values)

        self.setLayout(self.cameraSettingsLayout)

    def switch_to_sideview(self):
        self.sceneWidget.camera_entity.setUpVector(QVector3D(0, 1, 0))
        self.sceneWidget.current_camera_settings["position"] = QVector3D(30, 0, 0)
        self.sceneWidget.current_camera_settings["viewcenter"] = QVector3D(0, 0, 0)
        self.sceneWidget.switch_to_perspective()

    def switch_to_topview(self):
        self.sceneWidget.camera_entity.setUpVector(QVector3D(-1, 0, 0))
        self.sceneWidget.current_camera_settings["position"] = QVector3D(0, 30, 0)
        self.sceneWidget.current_camera_settings["viewcenter"] = QVector3D(0, 0, 0)
        self.sceneWidget.switch_to_perspective()

    def switch_to_frontview(self):
        self.sceneWidget.camera_entity.setUpVector(QVector3D(0, 1, 0))
        self.sceneWidget.current_camera_settings["position"] = QVector3D(0, 0, 30)
        self.sceneWidget.current_camera_settings["viewcenter"] = QVector3D(0, 0, 0)
        self.sceneWidget.switch_to_perspective()

    def initialize_default_values(self):
        self.positionVector_x_dsb.setValue(
            self.sceneWidget.default_camera_settings["position"].x()
        )
        self.positionVector_y_dsb.setValue(
            self.sceneWidget.default_camera_settings["position"].y()
        )
        self.positionVector_z_dsb.setValue(
            self.sceneWidget.default_camera_settings["position"].z()
        )
        self.viewCenterVector_x_dsb.setValue(
            self.sceneWidget.default_camera_settings["viewcenter"].x()
        )
        self.viewCenterVector_y_dsb.setValue(
            self.sceneWidget.default_camera_settings["viewcenter"].y()
        )
        self.viewCenterVector_z_dsb.setValue(
            self.sceneWidget.default_camera_settings["viewcenter"].z()
        )
        self.cameraSpeed_dsb.setValue(
            self.sceneWidget.default_camera_settings["cameraspeed"]
        )
        (
            fieldofview,
            aspectratio,
            nearfield,
            farfield,
        ) = self.sceneWidget.default_camera_settings["perspective"]
        self.fieldOfView_dsb.setValue(fieldofview)
        self.nearField_dsb.setValue(nearfield)
        self.farField_dsb.setValue(farfield)
        self.aspectRatio_1_dsb.setValue(16)
        self.aspectRatio_2_dsb.setValue(9)

    def read_current_values(self):
        self.positionVector_x_dsb.setValue(
            self.sceneWidget.camera_entity.position().x()
        )
        self.positionVector_y_dsb.setValue(
            self.sceneWidget.camera_entity.position().y()
        )
        self.positionVector_z_dsb.setValue(
            self.sceneWidget.camera_entity.position().z()
        )
        self.viewCenterVector_x_dsb.setValue(
            self.sceneWidget.camera_entity.viewCenter().x()
        )
        self.viewCenterVector_y_dsb.setValue(
            self.sceneWidget.camera_entity.viewCenter().y()
        )
        self.viewCenterVector_z_dsb.setValue(
            self.sceneWidget.camera_entity.viewCenter().z()
        )
        self.sceneWidget.gnomon.update_gnomon()

    def update_current_values(self):
        self.sceneWidget.current_camera_settings["position"] = QVector3D(
            self.positionVector_x_dsb.value(),
            self.positionVector_y_dsb.value(),
            self.positionVector_z_dsb.value(),
        )
        self.sceneWidget.current_camera_settings["viewcenter"] = QVector3D(
            self.viewCenterVector_x_dsb.value(),
            self.viewCenterVector_y_dsb.value(),
            self.viewCenterVector_z_dsb.value(),
        )
        self.sceneWidget.current_camera_settings["perspective"] = [
            self.fieldOfView_dsb.value(),
            self.aspectRatio_1_dsb.value() / self.aspectRatio_2_dsb.value(),
            self.nearField_dsb.value(),
            self.farField_dsb.value(),
        ]
        self.sceneWidget.current_camera_settings[
            "cameraspeed"
        ] = self.cameraSpeed_dsb.value()

        self.sceneWidget.switch_to_perspective()

    def set_default_settings(self):
        self.sceneWidget.camera_entity.setUpVector(QVector3D(0, 1, 0))
        self.initialize_default_values()
        self.update_current_values()
