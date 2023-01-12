from nodeeditor.node_node import Node
from nodeeditor.node_content_widget import  QDMNodeContentWidget
from nodeeditor.node_graphics_node import QDMGraphicsNode
from PyQt5.QtWidgets import *
from nodeeditor.node_socket import LEFT_BOTTOM,LEFT_TOP,RIGHT_TOP,RIGHT_BOTTOM
class KosGraphicsAllGrantedNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74
        self.edge_size = 5
        self._padding = 8

class KosGraphicsBaseNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 240
        self.height = 240
        self.edge_size = 5
        self._padding = 8

class KosBasicAllGrantedBaseNodeContent(QDMNodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class KosBasicBaseNodeContent(QDMNodeContentWidget):
    def initUI(self):
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)





class KosNode(Node):
    icon = ""
    op_code = 0
    op_title = "Undefined"
    content_label = ""
    content_label_objname = ""
    def __init__(self, scene,  inputs=[1], outputs=[1]):
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

    def initInnerClasses(self):
        self.content = KosBasicAllGrantedBaseNodeContent(self)
        self.grNode = KosGraphicsAllGrantedNode(self)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_TOP
        self.output_socket_position = RIGHT_TOP

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res
    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        return res
        #print('Deserialized CalcNode {} res:{}'.format(self.__class__.__name__, res))
