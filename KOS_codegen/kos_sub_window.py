from nodeeditor.node_editor_widget import NodeEditorWidget
from PyQt5.QtCore import *
from kos_conf import *
from PyQt5.QtGui import *
from kos_node_base import *
from nodeeditor.utils import dumpException

DEBUG = False
DEBUG_CONTEXT = False


class KOSSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setTitle()
        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)

        self._close_event_listeners = []
        self.scene.setNodeClassSelector(self.getNodeClassForData)

    def getNodeClassForData(self, data):
        if 'op_code' not in data: return Node
        return get_class_from_opcode(data['op_code'])

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFilename())

    def addCloseEventListener(self, callback):
        self._close_event_listeners.append(callback)

    def closeEvent(self, event):
        for callback in self._close_event_listeners: callback(self, event)

    def onDragEnter(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)
    def onDrop(self, event):
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData = event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            op_code = dataStream.readInt()
            text = dataStream.readQString()


            mouse_position = event.pos()
            scene_position = self.scene.getView().mapToScene(mouse_position)
            if DEBUG: print("got drop: {} {} mouse: {} scene: {}".format(op_code, text, mouse_position,scene_position))

            try:
                node = get_class_from_opcode(op_code)(self.scene)
                node.setPos(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Created node {}".format(node.__class__.__name__))
                self.scene._has_been_modified = True
                self.setWindowTitle(self.getUserFriendlyFilename())
            except Exception as e: dumpException(e)

            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()