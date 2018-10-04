import sys
from os import path
from PySide2.QtGui import QGuiApplication
from geometry_constructor import resources  # NOQA
from geometry_constructor.Window import Window

location = sys.executable if getattr(sys, 'frozen', False) else __file__
resource_folder = path.join(path.dirname(location), 'resources')

app = QGuiApplication(sys.argv)
view = Window(resource_folder)
view.show()
res = app.exec_()
del view
sys.exit(res)
