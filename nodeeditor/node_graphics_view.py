from PyQt5.QtWidgets import QGraphicsView, QApplication, QGraphicsTextItem, QInputDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodeeditor.node_graphics_edge import QDMGraphicsEdge
from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_edge import Edge, EDGE_TYPE_BEZIER
from nodeeditor.node_graphics_cutline import QDMCutLine
MODE_NOOP = 1
MODE_EDGE_DRAG = 2
EDGE_DRAG_START_THRESHOLD = 10
MODE_EDGE_CUT = 3
DEBUG = False


class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)


    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene
        self.initUI()
        self.setScene(self.grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)

        self._drag_enter_listeners = []
        self._drop_listeners = []

    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing
                            | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        for callback in self._drag_enter_listeners: callback(event)
    def dropEvent(self, event):
        for callback in self._drop_listeners: callback(event)

    def addDragEnterListener(self, callback):
        self._drag_enter_listeners.append(callback)

    def addDropListener(self, callback):
        self._drop_listeners.append(callback)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & -Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPress(self, event):


        item = self.getItemAtClick(event)
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())
        if DEBUG: print("LMB on {} {}".format(item, self.debug_modifiers(event)))
        if hasattr(item, "node") or isinstance(item,QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:

                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(),
                                        event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res : return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        # get item which clicked on
        item = self.getItemAtClick(event)
        # logic

        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(),
                                    event.screenPos(), Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGE_DRAG:

            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return


        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.line_points = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            return


        if self.rubberBandDraggingRectangle:
            self.rubberBandDraggingRectangle = False
            current_selected_items = self.grScene.selectedItems()
            if current_selected_items != self.grScene.scene._last_selected_items:
                if current_selected_items == []:
                    self.grScene.itemsDeselected.emit()
                else:
                    self.grScene.itemSelected.emit()
                self.grScene.scene._last_selected_items = current_selected_items

            return

        if item is None:
            self.grScene.itemsDeselected.emit()



        super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)
        item = self.getItemAtClick(event)
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print("RMB DEBUG: {} connecting sockets: {} <--> {}".format(
                item.edge, item.edge.start_socket, item.edge.end_socket))
            if type(item) is QDMGraphicsSocket: print("RMB DEBUG: {} has edge: {}".format(item.socket, item.socket.edges))

            if item is None:
                print('SCENE:')
                print(' Nodes')
                for node in self.grScene.scene.nodes: print('   {}'.format(node))
                print(' Edges')
                for edge in self.grScene.scene.edges: print('   {}'.format(edge))
        if type(item) is QGraphicsTextItem:
            if hasattr(item, "node"):
                if str(item.node.title) != "All Grant Node":
                    text, ok = QInputDialog.getText(self,'Input Dialog', 'Enter new node name:')
                    if ok:
                        item.node.title = text


    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.grEdge.setDestination(pos.x(), pos.y())
            self.drag_edge.grEdge.update()
        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.line_points.append(pos)
            self.cutline.update()
        self.last_scene_mouse_position = self.mapToScene(event.pos())
        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()), int(self.last_scene_mouse_position.y())
        )
        super().mouseMoveEvent(event)

#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_Delete:
#            if not self.editingFlag:
#                self.deleteSelected()
#            else:
#                super().keyPressEvent(event)
#        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
#            self.grScene.scene.saveToFile("graph.json")
#        elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
#            self.grScene.scene.loadFromFile("graph.json")
#        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
#            self.grScene.scene.history.undo()
#        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
#            self.grScene.scene.history.redo()
#        elif event.key() == Qt.Key_H:
#            print("History:       len({}) -- current_step {}".format(len(self.grScene.scene.history.history_stack), self.grScene.scene.history.history_current_step))
#            ix = 0
 #           for item in self.grScene.scene.history.history_stack:
#                print("#{} --- {}".format(ix, item['desc']))
 #               ix+=1
#
 #       else:
 #           super().keyPressEvent(event)

    def cutIntersectingEdges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()
        self.grScene.scene.history.storeHistory("Delete cutted selected", setModified=True)


    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()
        self.grScene.scene.history.storeHistory("Delete selected", setModified=True)


    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "Shift"
        if event.modifiers() & Qt.ControlModifier: out += "Ctrl"
        if event.modifiers() & Qt.AltModifier: out += "Alt"
        return out

    def getItemAtClick(self, event):
        # return object clicked

        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item):
        if DEBUG: print('View:edgeDragStart - Start dragging edge')
        if DEBUG: print('View:edgeDragStart -   assign Start socket to: {} '.format(item.socket))
        #self.previousEdge = item.socket.edges
        self.drag_start_socket = item.socket
        self.drag_edge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG: print("View:edgeDragStart -   dragEdge: {}".format(self.drag_edge))

    def edgeDragEnd(self, item):
        # return True if skip the rest of the code
        self.mode = MODE_NOOP
        if DEBUG: print('View:edgeDragEnd - End dragging edge')
        self.drag_edge.remove()
        self.drag_edge = None

        if type(item) is QDMGraphicsSocket:
            if item.socket != self.drag_start_socket:
               # if DEBUG: print('View:edgeDragEnd -     assign End Socket {}'.format(item.socket))

                #if DEBUG: print("View:edgeDragEnd -    previous edge : {}".format(self.previousEdge))
                #if item.socket.hasEdge():
                #    item.socket.edges.remove()
                if not item.socket.is_multi_edges:
                    item.socket.removeAllEdges()
                if not self.drag_start_socket.is_multi_edges:
                    self.drag_start_socket.removeAllEdges()

                #for edge in item.socket.edges:
                #    edge.remove()
               # if self.previousEdge is not None: self.previousEdge.remove()
                #if DEBUG: print("View:edgeDragEnd - previous edge removed")
                #self.drag_edge.start_socket = self.drag_start_socket

                #self.drag_edge.end_socket = item.socket
                #self.drag_edge.start_socket.addEdge(self.drag_edge)
                #self.drag_edge.end_socket.addEdge(self.drag_edge)
                #if DEBUG: print("View:edgeDragEnd -     reassigned start & end sockets to drag edge")
                #self.drag_edge.updatePositions()
                new_edge = Edge(self.grScene.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_BEZIER)
                if DEBUG: print('View:edgeDragEnd -     created new edge: {} connected to {} <--> {}'.format(new_edge, new_edge.start_socket,new_edge.end_socket))

                self.grScene.scene.history.storeHistory("Added new edge by dragging", setModified=True)
                return True



        #if DEBUG: print("View:edgeDragEnd - about to set socket to previous edge: {}".format(self.previousEdge))
        #if self.previousEdge is not None:
        #    self.previousEdge.start_socket.edges = self.previousEdge
        if DEBUG: print('View:edgeDragEnd - everything done')
        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD

        res = (dist_scene.x() * dist_scene.x() + dist_scene.y() * dist_scene.y()) > edge_drag_threshold_sq
        return res



    def wheelEvent(self, event):
        # calculate zoom factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate room
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:
            self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)
