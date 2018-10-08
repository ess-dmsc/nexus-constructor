from geometry_constructor.Application import Application
from geometry_constructor.Models import InstrumentModel
from system_tests.Helpers import click_object, tree_search_items
from PySide2.QtQuick import QQuickItem

"""
Tests for adding and removing items to the ListView's model through the GUI

While it is possible to call click events on items,
it does not appear that in this testing environment the
child items of the ListView get updated to reflect changes in the model.
As such, controls only exist for the initial data.

Additionally, QWindow's findChild() doesn't work on ListView children,
but they can still be navigated through the interface's parent-child tree structure
"""


# Test that clicking the 'add pixel' button adds an extra item to the model
def test_add_pixel_button(qtbot):
    main = Application('resources')
    window = main.rootObjects()[0]
    qtbot.addWidget(window)
    assert window.findChild(InstrumentModel, 'components').rowCount() == 1
    click_object(window.findChild(QQuickItem, 'addDetector'), window)
    assert window.findChild(InstrumentModel, 'components').rowCount() == 2


# Test that clicking the first 'remove' button takes an item from the model
def test_remove_pixel_button(qtbot):
    main = Application('resources')
    window = main.rootObjects()[0]
    assert window.findChild(InstrumentModel, 'components').rowCount() == 1
    pixels = window.findChild(QQuickItem, 'componentListView')
    click_object(tree_search_items(pixels, 'removalButton'), window)
    assert window.findChild(InstrumentModel, 'components').rowCount() == 0
