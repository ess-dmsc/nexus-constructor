"""
Classes for modelling json so its lines can be used as a listview model in QML

Json is formatted with consistent indents and ordered keys when inserted into the model.
To give a condensed view, lines of text comprising lists of numbers are combined into a single line.
"""

import attr
import json
import re
from PySide2.QtCore import (
    Qt,
    QAbstractListModel,
    QModelIndex,
    QSortFilterProxyModel,
    Signal,
    Slot,
)


@attr.s
class JsonLine:
    """
    A collapsible representation of a line in a pretty printed json file

    text: the full text of the line
    collapsed_text: if the full text of the line ends by opening a list or object, this should have an appended
        representation of that item, such as [...] or {...}
    collapsed: whether in the current GUI this line should be shown as collapsed or full
    line_number: the line number this object represents in the formatted json. Differentiates between lines with
                 identical text when determining parents
    parent: the JsonLine representing the start of the list or object this line is part of
    """

    text = attr.ib(default="")
    collapsed_text = attr.ib(default="")
    collapsed = attr.ib(default=False)
    line_number = attr.ib(default=0)
    parent = attr.ib(default=None)

    @property
    def indent(self):
        """The number of spaces padding the start of the line"""
        return len(self.text) - len(self.text.lstrip(" "))

    @property
    def visible(self):
        """Whether a line in this line's parent hierarchy is collapsed"""
        if self.parent is None:
            return True
        elif self.parent.collapsed:
            return False
        else:
            return self.parent.visible


class JsonModel(QAbstractListModel):
    """
    A list model for providing QML access to the formatted lines of a json file

    Guidance on how to correctly extend QAbstractListModel, including method signatures and required signals can be
    found at http://doc.qt.io/qt-5/qabstractlistmodel.html#subclassing
    """

    TextRole = Qt.UserRole + 300
    CollapsedRole = Qt.UserRole + 301
    CollapsedTextRole = Qt.UserRole + 302
    VisibleRole = Qt.UserRole + 303

    def __init__(self, parent=None):
        super().__init__(parent)
        self.indent_level = 2
        self.lines = [JsonLine(text="[\n  1, 2, 3\n]", collapsed_text="[...]")]

    def rowCount(self, parent=QModelIndex()):
        return len(self.lines)

    def roleNames(self):
        return {
            JsonModel.TextRole: b"full_text",
            JsonModel.CollapsedRole: b"collapsed",
            JsonModel.CollapsedTextRole: b"collapsed_text",
            JsonModel.VisibleRole: b"line_visible",
        }

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        line = self.lines[row]
        accessors = {
            JsonModel.TextRole: line.text,
            JsonModel.CollapsedRole: line.collapsed,
            JsonModel.CollapsedTextRole: line.collapsed_text,
            JsonModel.VisibleRole: line.visible,
        }
        if role in accessors:
            return accessors[role]

    def setData(self, index, value, role):
        row = index.row()
        item = self.lines[row]
        changed = False
        attributes = {
            JsonModel.TextRole: "text",
            JsonModel.CollapsedRole: "collapsed",
            JsonModel.CollapsedTextRole: "collapsed_text",
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
        """
        Replaces the current json in the model with new data, formatted from the given json string

        :param json_data: The json string to populate this model with
        """
        self.beginResetModel()

        json_lines = []
        # prettify and sort the json, then split it into lines
        lines = json.dumps(
            json.loads(json_data), indent=self.indent_level, sort_keys=True
        ).split("\n")
        collecting = False
        collection = []

        def store_collection(collapse=False):
            """Stores the strings in the collection list as JsonLines in json_lines

            :param collapse: Whether to store the collected strings as a single JsonLine
            """
            if collapse:
                line = JsonLine(
                    text="{}{}{}".format(
                        collection[0],
                        " ".join([ln.strip() for ln in collection[1:-1]]),
                        collection[-1].strip(),
                    ),
                    collapsed_text="{}...{}".format(
                        collection[0], collection[-1].strip()
                    ),
                    line_number=len(json_lines),
                )
                assign_parent(line)
                json_lines.append(line)
            else:
                for stored_line in collection:
                    if stored_line.endswith("["):
                        collapsed_text = stored_line + "...]"
                    elif stored_line.endswith("{"):
                        collapsed_text = stored_line + "...}"
                    else:
                        collapsed_text = stored_line
                    line = JsonLine(
                        text=stored_line,
                        collapsed_text=collapsed_text,
                        line_number=len(json_lines),
                    )
                    assign_parent(line)
                    json_lines.append(line)
            collection.clear()

        # The first line shouldn't have a parent
        latest_line_at_indent = {-self.indent_level: None}

        def assign_parent(line: JsonLine):
            """Set the line's parent based on the indent level of previous lines"""
            indent = line.indent
            closes = re.match("^[]}],?$", line.text.strip())
            parent_indent = indent if closes else indent - self.indent_level
            line.parent = latest_line_at_indent[parent_indent]
            latest_line_at_indent[indent] = line

        # if a line ends in a '[' and subsequent lines before its ']' only contain numbers,
        # combine those lines into a single JsonLine
        for i in range(len(lines)):
            line = lines[i]
            if line.endswith("["):
                store_collection()
                collection.append(line)
                collecting = True
            elif collecting:
                collection.append(line)
                # end of a list
                if re.match("],?$", line.strip()):
                    store_collection(collapse=True)
                    collecting = False
                # list isn't just numbers
                elif not re.match("^-?\d*\.?\d*,?$", line.strip()):
                    store_collection()
                    collecting = False
            else:
                collection.append(line)
        store_collection()

        # add any required trailing commas to collapsed text
        for line in json_lines:
            if line.text.endswith(("[", "{")):
                # find its last child
                last_child = None
                for candidate_child in json_lines:
                    if candidate_child.parent == line:
                        last_child = candidate_child
                if last_child.text.endswith(","):
                    line.collapsed_text += ","

        self.lines = json_lines
        self.endResetModel()

    def signal_child_visibilities_updated(self, line: JsonLine):
        line_index = self.lines.index(line)
        for i in range(line_index + 1, len(self.lines)):
            candidate_closer = self.lines[i]
            if candidate_closer.indent == line.indent:
                self.dataChanged.emit(
                    self.createIndex(line_index + 1, 0),
                    self.createIndex(i, 0),
                    JsonModel.VisibleRole,
                )
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
        self.setFilterFixedString("True")

    @Slot(str)
    def set_json(self, json_data):
        self.json_updated.emit(json_data)
