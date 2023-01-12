import os.path

from PyQt5.QtWidgets import QFileDialog

from nodeeditor.utils import dumpException
from nodeeditor.node_graphics_scene import QDMGrapicsScene
from nodeeditor.node_serializable import Serializable
from collections import OrderedDict
from nodeeditor.node_node import Node
from nodeeditor.node_edge import  Edge
from nodeeditor.node_scene_history import SceneHistory
from nodeeditor.node_scene_clipboard import SceneClipboard

import json

class InvalidFile(Exception): pass

class Scene(Serializable):

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width = 64000
        self.scene_height = 64000

        self._has_been_modified = False
        self._last_selected_items = []

        self._has_been_modified_listeners = []
        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        #store callback for retrueve class for node
        self.node_class_selector = None

        self.initUI()
        self.history = SceneHistory(self)

        self.clipboard = SceneClipboard(self)
        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

    def initUI(self):
        self.grScene = QDMGrapicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def onItemSelected(self):
        #print("SCENE:: -onItemSelected")
        current_selected_items = self.getselectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            #self.history.storeHistory("Selection Changed")
            for callback in self._item_selected_listeners: callback()

    def onItemsDeselected(self):
        #print("SCENE:: -onItemsDeselected")
        self.resetLastSelectedStates()
        if self._last_selected_items != []:
            self._last_selected_items = []
            #self.history.storeHistory("Deselected Everything")
            for callback in self._items_deselected_listeners: callback()


    @property
    def has_been_modified(self):
        #return False# 
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:

            self._has_been_modified = value
            for callback in self._has_been_modified_listeners:
                callback()
        self._has_been_modified = value

    def isModified(self):
        return self.has_been_modified

    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback):
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self,callback):
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.getView().addDropListener(callback)

    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def getView(self):
        return self.grScene.views()[0]

    def getItemAt(self, pos):
        self.getView().itemAt(pos)


    def getselectedItems(self):
        return self.grScene.selectedItems()

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print("!WZ:   Scene::removenode: trying remove: {}. Not at list".format(node))

    def removeEdge(self, edge):
        #self.edges.remove(edge)
        if edge in self.edges:
            self.edges.remove(edge)
    #    else:
       #     print("!WZ:   Scene::removeedge: trying remove: {}. Not at list".format(edge))

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self._has_been_modified = False

    def saveToFile(self, filename):
        #if filename is None: filename = "New graph"
        with open(filename, "w") as file:
            file.write( json.dumps(self.serialize(), indent=4 ))
            print("saving to {} was successfull".format(filename))

            self._has_been_modified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf-8')
                self.deserialize(data)
                self._has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile("{} is not a valid JSON file".format(os.path.basename(filename)))
            except Exception as e:
                dumpException(e)

    def setNodeClassSelector(self, class_selecting_function):
        self.node_class_selector = class_selecting_function

    def getNodeClassFormData(self, data):
        return Node if self.node_class_selector is None else self.node_class_selector(data)


    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges)
        ])

    def deserialize(self, data, hashmap=[], restore_id = True):
        self.clear()
        hashmap = {}
        if restore_id: self.id = data['id']
        # create nodes
        for node_data in data['nodes']:
            self.getNodeClassFormData(node_data)(self).deserialize(node_data, hashmap, restore_id)

        # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        return True