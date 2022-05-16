from functools import partial

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel
from PySide2.QtCore import Signal

from nexus_constructor.model.module import StreamModules, WriterModules, WriterModuleClasses
from nexus_constructor.model.writer_module_container import ModuleContainer
from nexus_constructor.ui_utils import line_edit_validation_result_handler
from nexus_constructor.validators import NoEmptyStringValidator, MultiItemValidator
from nexus_constructor.widgets.streamer_extra_config import ADArExtraConfig, F142ExtraConfig, Ev42ExtraConfig

extra_config_map = {StreamModules.ADAR.value: ADArExtraConfig,
                    StreamModules.EV42.value: Ev42ExtraConfig,
                    StreamModules.F142.value: F142ExtraConfig,
                    }


class FileWriterModuleEdit(QWidget):
    def __init__(self, parent: QWidget, container: ModuleContainer):
        super().__init__(parent)
        self._second_line_widget = None
        self._module_container = container
        self._first_line_layout = QHBoxLayout()
        self._first_line_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._module_type_combo: QComboBox = QComboBox(self)
        self._module_type_combo.addItems([m.value for m in StreamModules])
        self._module_type_combo.setCurrentText(container.module.writer_module)

        self._topic_edit = QLineEdit(self)
        self._topic_edit.setPlaceholderText("Topic")
        self._topic_edit.setValidator(NoEmptyStringValidator())
        self._source_edit = QLineEdit(self)
        self._source_edit.setPlaceholderText("Source name")
        self._source_edit.setValidator(NoEmptyStringValidator())

        self._more_options = QPushButton("More")
        self._more_options.setEnabled(False)
        self._more_options.clicked.connect(self._handle_more_or_less)

        self._first_line_layout.addWidget(self._module_type_combo)
        self._first_line_layout.addWidget(self._topic_edit)
        self._first_line_layout.addWidget(self._source_edit)
        self._first_line_layout.addWidget(self._more_options)
        self.layout().addLayout(self._first_line_layout)

        self._module_validator = MultiItemValidator()

        self._topic_edit.validator().is_valid.connect(
            partial(self._module_validator.set_is_valid, self._topic_edit)
        )
        self._source_edit.validator().is_valid.connect(
            partial(self._module_validator.set_is_valid, self._source_edit)
        )

        self._topic_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._topic_edit,
            )
        )

        self._source_edit.validator().is_valid.connect(
            partial(
                line_edit_validation_result_handler,
                self._source_edit,
            )
        )
        self._module_validator.is_valid.connect(self.is_valid.emit)

        self._topic_edit.setText(self._module_container.module.topic)
        self._source_edit.setText(self._module_container.module.source)
        self._topic_edit.textEdited.connect(self._topic_edited)
        self._source_edit.textEdited.connect(self._source_edited)

        self._module_type_combo.currentIndexChanged.connect(self._handle_module_change)

        self._populate_extra_attributes()

    def _handle_module_change(self, new_index: int):
        module_map = {WriterModules.F142.value: WriterModuleClasses.F142,
                      WriterModules.EV42.value: WriterModuleClasses.EV42,
                      WriterModules.TDCTIME.value: WriterModuleClasses.TDCTIME,
                      WriterModules.NS10.value: WriterModuleClasses.NS10,
                      WriterModules.SENV.value: WriterModuleClasses.SENV,
                      WriterModules.HS00.value: WriterModuleClasses.HS00,
                      WriterModules.ADAR.value: WriterModuleClasses.ADAR,
                      }
        c_module_type = self._module_container.module.writer_module
        new_module_type = self._module_type_combo.itemText(new_index)
        if c_module_type != new_module_type:
            new_module = module_map[new_module_type].value(parent_node=self._module_container.module.parent_node, topic=self._module_container.module.topic, source=self._module_container.module.source)
            module_index = self._module_container.module.parent_node.children.index(self._module_container.module)
            self._module_container.module.parent_node.children[module_index] = new_module
            self._module_container.module = new_module
            self._populate_extra_attributes()

    def _handle_more_or_less(self):
        self._module_container.module.expanded = not self._module_container.module.expanded
        if self._module_container.module.expanded:
            self._more_options.setText("Less")
            self._second_line_widget.show()
        else:
            self._more_options.setText("More")
            self._second_line_widget.hide()
        self.sizeHintChanged.emit()

    def _populate_extra_attributes(self):
        if self._second_line_widget is not None:
            self._second_line_widget.hide()
            self._second_line_layout.removeWidget(self._second_line_widget)
            self._second_line_widget = None
        if hasattr(self._module_container.module, "expanded"):
            self._more_options.setEnabled(True)
            self._second_line_layout = QHBoxLayout()
            self._second_line_layout.setContentsMargins(0, 0, 0, 0)
            self._second_line_widget = extra_config_map[self._module_container.module.writer_module](self, self._module_container)
            self._second_line_widget.is_valid.connect(partial(self._module_validator.set_is_valid, self._second_line_widget))
            self._second_line_widget.check_validity()
            self._second_line_layout.addWidget(self._second_line_widget)
            self.layout().addLayout(self._second_line_layout)
            if self._module_container.module.expanded:
                self._more_options.setText("Less")
                self._second_line_widget.show()
            else:
                self._more_options.setText("More")
                self._second_line_widget.hide()
        else:
            self._more_options.setText("More")
            self._more_options.setEnabled(False)
        self.sizeHintChanged.emit()

    def _source_edited(self, new_source: str):
        self._module_container.module.source = new_source

    def _topic_edited(self, new_topic: str):
        self._module_container.module.topic = new_topic

    def check_validity(self):
        self._topic_edit.validator().validate(self._topic_edit.text(), 0)
        self._source_edit.validator().validate(self._source_edit.text(), 0)

    is_valid = Signal(bool)
    sizeHintChanged = Signal()
