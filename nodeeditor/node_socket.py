from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_serializable import Serializable
from collections import OrderedDict
LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4

DEBUG = False

class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1, multi_edges=True):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.is_multi_edges = multi_edges
        if DEBUG: print("Socket -- creating with {} {} for node {}".format(self.index, self.position, self.node))

        self.grSocket = QDMGraphicsSocket(self, self.socket_type)

        self.grSocket.setPos(*self.node.getSocketPosition(index, position))

        self.edges = []

    #def __str__(self):
     #   return "<Socket %s %s...%s>" % ("ME" if self.is_multi_edges else "SE", hex(id(self))[2:5], hex(id(self))[-3:])



    def getSocketPosition(self):
        if DEBUG: print(" GSP: {} {} Node: {}".format(self.index, self.position, self.node))
        return self.node.getSocketPosition(self.index, self.position)



    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
       # else:
      #      print("!WZ:   Socket::removeedge: trying remove: {}. Not at list".format(edge))

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()
        #self.edges.clear()
    #def hasEdge(self):
    #    return self.edges is not None

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ("multi_edges", self.is_multi_edges),
            ('position', self.position),
            ('type', self.socket_type),
        ])

    def determineMultiEdges(self, data):
        if 'multi_edges' in data:
            return data['multi_edges']
        else:
            return data['position'] in [RIGHT_BOTTOM,RIGHT_TOP]

    def deserialize(self, data, hashmap=[], restore_id=True):
        if  restore_id: self.id = data["id"]
        self.is_multi_edges = self.determineMultiEdges(data)

        hashmap[data['id']] = self

        return True