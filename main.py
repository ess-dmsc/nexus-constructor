import sys
from os import path, environ
from PySide2.QtGui import QGuiApplication
from geometry_constructor.Window import Window

location = sys.executable if getattr(sys, 'frozen', False) else __file__
resource_folder = path.join(path.dirname(location), 'resources')

environ['QT_QUICK_CONTROLS_CONF'] = path.join(resource_folder, 'qtquickcontrols2.conf')

app = QGuiApplication(sys.argv)
view = Window(resource_folder)
view.show()
res = app.exec_()
del view
sys.exit(res)
