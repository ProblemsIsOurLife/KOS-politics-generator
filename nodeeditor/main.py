# This is a sample Python script.
import sys

from PyQt5.QtWidgets import *
from node_editor_window import NodeEditorWindow
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = NodeEditorWindow()
    wnd.nodeeditor.addNodes()
    sys.exit(app.exec_())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
