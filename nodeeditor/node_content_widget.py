from PyQt5.QtWidgets import *
from nodeeditor.node_serializable import Serializable
from collections import OrderedDict

class QDMNodeContentWidget(QWidget, Serializable):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.initUI()

    def initUI(self):
        #self.layout = QVBoxLayout()
        #self.layout.setContentsMargins(0, 0, 0, 0)
        #self.setLayout(self.layout)

        #self.wdg_label = QLabel("SomeTitle")
        #self.layout.addWidget(self.wdg_label)
        #self.layout.addWidget(QDMTextEdit("foo"))
        pass

    def isModified(self):
        return self.scene.has_been_modified


    def setEditingFlag(self, value):
        self.node.scene.getView().editingFlag = value

    def serialize(self):
        return OrderedDict([



        ])
    def deserialize(self, data, hashmap=[]):
        return True
        #return OrderedDict([
#
        #])

class QDMTextEdit(QTextEdit):

    def focusInEvent(self, event):
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
