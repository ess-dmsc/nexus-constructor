"""
Classes for modelling json and including it as a model for a listview in QML

json is formatted with consistent indents and ordered keys when inserted into the model.
To give a condensed view, lines of text comprising lists of numbers are combined into a single line.
"""

import attr
import json
import re
from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex, QSortFilterProxyModel, Signal, Slot


@attr.s
class JsonLine:
    """
    A collapsible representation of a line in a pretty printed json file

    text: the full text of the line
    collapsed_text: if the full text of the line ends by opening a list or object, this should have an appended
        representation of that item, such as [...] or {...}
    collapsed: whether in the current GUI this line should be shown as collapsed or full
    indent: the number of spaces padding the start of the line
    parent: the JsonLine representing the start of the list or object this line is part of

    visible: whether a line in this line's parent hierarchy is collapsed
    """
    text = attr.ib(default='')
    collapsed_text = attr.ib(default='')
    collapsed = attr.ib(default=False)
    line_number = attr.ib(default=0)
    parent = attr.ib(default=None)

    @property
    def indent(self):
        return len(self.text) - len(self.text.lstrip(' '))

    @property
    def visible(self):
        if self.parent is None:
            return True
        elif self.parent.collapsed:
            return False
        else:
            return self.parent.visible


class JsonModel(QAbstractListModel):
    """
    A list model for providing QML access to a list of lines in a pretty printed json file

    Guidance on how to correctly extend QAbstractListModel, including method signatures and required signals can be
    found at http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    """

    TextRole = Qt.UserRole + 300
    CollapsedRole = Qt.UserRole + 301
    CollapsedTextRole = Qt.UserRole + 302
    VisibleRole = Qt.UserRole + 303

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = [
            JsonLine(text='[\n1, 2, 3\n]', collapsed_text='[...]')
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self.lines)

    def roleNames(self):
        return {
            JsonModel.TextRole: b'full_text',
            JsonModel.CollapsedRole: b'collapsed',
            JsonModel.CollapsedTextRole: b'collapsed_text',
            JsonModel.VisibleRole: b'line_visible',
        }

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        line = self.lines[row]
        accessors = {
            JsonModel.TextRole: line.text,
            JsonModel.CollapsedRole: line.collapsed,
            JsonModel.CollapsedTextRole: line.collapsed_text,
            JsonModel.VisibleRole: line.visible
        }
        if role in accessors:
            return accessors[role]

    def setData(self, index, value, role):
        row = index.row()
        item = self.lines[row]
        changed = False
        attributes = {
            JsonModel.TextRole: 'text',
            JsonModel.CollapsedRole: 'collapsed',
            JsonModel.CollapsedTextRole: 'collapsed_text',
        }
        if role in attributes:
            attribute_name = attributes[role]
            current_value = getattr(item, attribute_name)
            changed = value != current_value
            if changed:
                setattr(item, attribute_name, value)
                self.dataChanged.emit(index, index, role)
                if role == JsonModel.CollapsedRole:
                    self.signal_child_visibilities_updated(item)
        return changed

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    @Slot(str)
    def set_json(self, json_data):
        self.beginResetModel()

        json_lines = []
        # prettify the json and split it into lines
        lines = json.dumps(json.loads(json_data), indent=2, sort_keys=True).split('\n')
        collecting = False
        collection = []

        def store_collection(collapse=False):
            if collapse:
                json_lines.append(
                    JsonLine(
                        text=collection[0]
                        + ' '.join([ln.strip() for ln in collection[1:-1]])
                        + collection[-1].strip(),
                        collapsed_text=collection[0] + '...' + collection[-1].strip(),
                        line_number=len(json_lines)
                    ))
            else:
                for stored_line in collection:
                    if stored_line.endswith('['):
                        collapsed_text = stored_line + '...]'
                    elif stored_line.endswith('{'):
                        collapsed_text = stored_line + '...}'
                    else:
                        collapsed_text = stored_line
                    json_lines.append(JsonLine(text=stored_line,
                                               collapsed_text=collapsed_text,
                                               line_number=len(json_lines)
                                               ))
            collection.clear()
        # if a line ends in a '[' and subsequent lines before its ']' only contain numbers,
        # combine those lines into a single JsonLine
        for i in range(len(lines)):
            line = lines[i]
            if line.endswith('['):
                store_collection()
                collection.append(line)
                collecting = True
            elif collecting:
                collection.append(line)
                if re.match('],?$', line.strip()):  # end of a list
                    store_collection(collapse=True)
                    collecting = False
                elif not re.match('^-?\d*\.?\d*,?$', line.strip()):  # list isn't just numbers
                    store_collection()
                    collecting = False
            else:
                collection.append(line)
        store_collection()

        # for each non root level line in the json, set its parent
        for i in range(1, len(json_lines)):
            child = json_lines[i]
            lists = 0
            objects = 0
            for candidate_index in range(i - 1, -1, -1):
                candidate_parent = json_lines[candidate_index]
                is_list_end = re.match('^],?$', candidate_parent.text.strip())
                is_list_start = candidate_parent.text.endswith('[')
                is_obj_end = re.match('^},?$', candidate_parent.text.strip())
                is_obj_start = candidate_parent.text.endswith('{')
                if (is_obj_start or is_list_start) and lists == 0 and objects == 0:
                    child.parent = candidate_parent
                    break
                if is_list_end:
                    lists -= 1
                if is_list_start:
                    lists += 1
                if is_obj_end:
                    objects -= 1
                if is_obj_start:
                    objects += 1

        # add any required trailing commas to collapsed text
        for line in json_lines:
            if line.text.endswith(('[', '{')):
                # find its last child
                last_child = None
                for candidate_child in json_lines:
                    if candidate_child.parent == line:
                        last_child = candidate_child
                if last_child.text.endswith(','):
                    line.collapsed_text += ','

        self.lines = json_lines
        self.endResetModel()

    def signal_child_visibilities_updated(self, line: JsonLine):
        line_index = self.lines.index(line)
        for i in range(line_index + 1, len(self.lines)):
            candidate_closer = self.lines[i]
            if candidate_closer.indent == line.indent:
                self.dataChanged.emit(self.createIndex(line_index + 1, 0),
                                      self.createIndex(i, 0),
                                      JsonModel.VisibleRole)
                return


class FilteredJsonModel(QSortFilterProxyModel):
    """
    A filtered wrapper for the JsonModel class, only providing visible lines to the view
    """

    json_updated = Signal(str)

    def __init__(self):
        super().__init__()
        json_model = JsonModel()
        self.json_updated.connect(json_model.set_json)
        self.setSourceModel(json_model)
        self.setFilterRole(JsonModel.VisibleRole)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterFixedString('True')

    @Slot(str)
    def set_json(self, json):
        self.json_updated.emit(json)
