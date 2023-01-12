from PyQt5.QtCore import Qt, QFile
import os
from PyQt5.QtWidgets import *
from nodeeditor.node_graphics_scene import QDMGrapicsScene

from PyQt5.QtGui import *
from nodeeditor.node_graphics_view import QDMGraphicsView
from nodeeditor.node_scene import Scene,InvalidFile
from nodeeditor.node_node import Node
from nodeeditor.node_edge import Edge, EDGE_TYPE_BEZIER

class NodeEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None
        self.initUI()

    def initUI(self):

        self.layout=QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


        #graphic scene
        self.scene = Scene()
        #self.grScene = self.scene.grScene
        #self.addNodes()

        #graphic view
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        #self.addDebugContent()

    def isFilenameSet(self):
        return self.filename is not None
    def isModified(self):
        return self.scene.has_been_modified

    def getSelectedItems(self):
        return self.scene.getselectedItems()

    def hasSelectedItems(self):
        return self.getSelectedItems() != []

    def canUndo(self):
        return self.scene.history.canUndo()
    def canRedo(self):
        return self.scene.history.canRedo()

    def fileNew(self):
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def getUserFriendlyFilename(self):
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"

        return name + ("*" if self.isModified() else "")

    def fileload(self, filename):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            QApplication.restoreOverrideCursor()
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except InvalidFile as e:
            print(e)
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading {}".format(os.path.basename(filename)),str(e))

            return False
        finally:
            QApplication.restoreOverrideCursor()
        return False

    def filesave(self, filename=None):
        if filename is not None:
            self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True

    def addNodes(self):
        node1 = Node(self.scene, "My Awesome Node", inputs=[1, 2, 3], outputs=[1])
        node2 = Node(self.scene, "My Awesome Node 2", inputs=[1, 2, 3], outputs=[1])
        node3 = Node(self.scene, "My Awesome Node 3", inputs=[1, 2, 3], outputs=[1])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[1], edge_type=EDGE_TYPE_BEZIER)

        self.scene.history.storeInitialHistoryStamp()  # maybe not needed

