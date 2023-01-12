from kos_conf import *
from kos_node_base import *
from PyQt5.QtCore import *

from nodeeditor.utils import dumpException


@register_node(OP_NODE_ALL_GRANTED)
class KosNode_AllGrant(KosNode):
    icon = ""
    op_code = OP_NODE_ALL_GRANTED
    op_title = "All Grant Node"
    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
    def initInnerClasses(self):
        self.content = KosBasicAllGrantedBaseNodeContent(self)
        self.grNode = KosGraphicsAllGrantedNode(self)


class KosBasicAllGrantedBaseNodeContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLabel("Set Granted to all", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)
        content_label_objname = "request"


@register_node(OP_NODE_BASE_WIDGET)
class KosNode_BaseWidget(KosNode):
    icon = ""
    op_code = OP_NODE_BASE_WIDGET
    op_title = "Basic Name"
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[2,3])
        self._title = self.op_title
    def initInnerClasses(self):
        self.content = KosBasicBaseNodeContent(self)
        self.grNode = KosGraphicsBaseNode(self)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title

class KosBasicBaseNodeContent(QDMNodeContentWidget):
    def initUI(self):
        self.accept = QLabel("Connect to accept by this node", self)
        self.accept.setObjectName("Accept")


        self.response = QLabel("Response", self)
        self.response.setObjectName("Response")

        self.request = QLabel("Request", self)
        self.request.setObjectName("Request")

        self.endpoint = QLabel("Endpoint", self)
        self.endpoint.setObjectName("Endpoint")

        self.edit_endpoint = QLineEdit("", self)
        self.edit_endpoint.setAlignment(Qt.AlignLeft)
        self.edit_endpoint.setObjectName("Edit_Endpoint")
        self.edit_endpoint.setGeometry(60, 60, 155, 25)

        self.method = QLabel("Method", self)
        self.method.setObjectName("Method")

        self.edit_method = QLineEdit("", self)
        self.edit_method.setAlignment(Qt.AlignLeft)
        self.edit_method.setObjectName("Edit_Method")
        self.edit_method.setGeometry(60, 120, 155, 25)

        self.set_assert = QLabel("Assert", self)
        self.set_assert.setObjectName("Assert")

        #self.set_assert.setGeometry(5, 160, 60, 30)

        self.edit_set_assert = QLineEdit("", self)
        self.edit_set_assert.setAlignment(Qt.AlignLeft)
        #self.edit_set_assert.setGeometry()
        self.edit_set_assert.setGeometry(60, 175,155,25)
        self.edit_set_assert.setObjectName("Edit_Assert")


    def serialize(self):
        res = super().serialize()
        res['endpoint_data'] = self.edit_endpoint.text()
        res['method_data'] = self.edit_method.text()
        res['assert_data'] = self.edit_set_assert.text()
        return res

    def deserialize(self, data, hashmap=[]):
        res = super().deserialize(data, hashmap)
        try:
            enpoint_value = data['endpoint_data']
            self.edit_endpoint.setText(enpoint_value)
            method_value = data['method_data']
            self.edit_method.setText(method_value)
            assert_value = data['assert_data']
            self.edit_set_assert.setText(assert_value)
            return True & res
        except Exception as e: dumpException(e)
        return res


#register node using function call
#register_node_now(OP_NODE_ALL_GRANTED, KosNode_Add)