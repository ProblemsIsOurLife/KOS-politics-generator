from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.node_socket import Socket, RIGHT_TOP, RIGHT_BOTTOM, LEFT_TOP, LEFT_BOTTOM
from nodeeditor.node_serializable import Serializable
from collections import OrderedDict

from nodeeditor.utils import dumpException

DEBUG = False

class Node(Serializable):
    def __init__(self, scene, title="Undefined Node", inputs=[], outputs=[]):
        super().__init__()
        self._title = title
        self.scene = scene

        self.initInnerClasses()
        self.initSettings()
        self.title = title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        # create sockets for in and out puts
        #self.grNode.title = "asdd"
        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)


    def __str__(self):
        return "<Node %s...%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    @property
    def pos(self):
        return self.grNode.pos()

    def setPos(self, x, y):
        self.grNode.setPos(x, y)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title


    def initInnerClasses(self):
        self.content = QDMNodeContentWidget(self)
        self.grNode = QDMGraphicsNode(self)

    def initSettings(self):
        self.socket_spacing = 22
        self.input_socket_position = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.input_multi_edged = True
        self.output_multi_edged = True

    def initSockets(self, inputs, outputs, reset=True):
        if reset:
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                for socket in (self.inputs+self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs= []

        counter = 0
        for item in inputs:
            socket = Socket(node=self, index=counter, position=self.input_socket_position, socket_type=item,
                            multi_edges=self.input_multi_edged)
            counter += 1
            self.inputs.append(socket)
        counter = 0
        for item in outputs:
            socket = Socket(node=self, index=counter, position=self.output_socket_position, socket_type=item,
                            multi_edges=self.output_multi_edged)
            counter += 1
            self.outputs.append(socket)


    def getSocketPosition(self, index, position):
        x = 0 if position in (LEFT_TOP, LEFT_BOTTOM) else self.grNode.width
        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # start from bottom
            y = self.grNode.height - self.grNode.edge_size - self.grNode._padding - index * self.socket_spacing
        else:
            if index == 0 and position == LEFT_TOP:
                y = self.grNode.title_height * 1.75 + self.grNode._padding + self.grNode.edge_size + index * self.socket_spacing
                return [x, y]
            if index == 1:
                y = self.grNode.title_height + self.grNode._padding + self.grNode.edge_size + index * self.socket_spacing * 1.25
                return [x, y]
            if index == 2:
                y = self.grNode.title_height + self.grNode._padding + self.grNode.edge_size + index * self.socket_spacing * 2.75
                return [x, y]
            y = self.grNode.title_height + self.grNode._padding + self.grNode.edge_size + index * self.socket_spacing

        return [x, y]



    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            #if socket.hasEdge():
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        if DEBUG: print("> Removing Node {}".format(self))
        if DEBUG: print(" - remove all edges from socket")
        for socket in (self.inputs + self.outputs):
            #if socket.hasEdge():
            for edge in socket.edges:
                if DEBUG: print(" - removing socket: {}  edges: {}".format(socket, edge))
                edge.remove()
        if DEBUG: print(" - remove grNode")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG: print(" - remove node from scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - everything done")

    def serialize(self):
        inputs, outputs = [], []
        for sockets in self.inputs: inputs.append(sockets.serialize())
        for sockets in self.outputs: outputs.append(sockets.serialize())
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', self.content.serialize()),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        try:
            if restore_id: self.id = data["id"]
            hashmap[data['id']] = self

            self.setPos(data['pos_x'], data['pos_y'])

            self.title = data['title']

            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)

            self.inputs = []
            for socket_data in data['inputs']:
                new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                    socket_type=socket_data['type'])
                new_socket.deserialize(socket_data, hashmap, restore_id)
                self.inputs.append(new_socket)

            self.outputs = []
            for socket_data in data['outputs']:
                new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                    socket_type=socket_data['type'])
                new_socket.deserialize(socket_data, hashmap, restore_id)
                self.outputs.append(new_socket)

        except Exception as e: dumpException(e)

        res = self.content.deserialize(data['content'], hashmap)
        return True & res