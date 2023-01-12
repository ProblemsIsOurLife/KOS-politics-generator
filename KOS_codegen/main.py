import sys, os
import inspect
from PyQt5.QtWidgets import *
from kos_window import KOSWindow
from nodeeditor.utils import loadStyleSheet

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    wnd = KOSWindow()

    module_path = os.path.dirname(inspect.getfile(wnd.__class__))
    loadStyleSheet(os.path.join(module_path, 'qss/nodeeditor.qss'))
    wnd.show()
    sys.exit(app.exec_())