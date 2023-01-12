from collections import OrderedDict
from nodeeditor.node_node import Node
from nodeeditor.node_edge import Edge
from nodeeditor.node_graphics_edge import QDMGraphicsEdge

DEBUG = True
class SceneClipboard():
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        if DEBUG: print('--- Copy to clipboard ---')

        sel_nodes, sel_edges, sel_sockets,sel_sockets_info = [], [], [], []
        # sort edges and nodes

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    #sel_sockets[socket.id] = socket
                    #print(socket.id)
                    sel_sockets.append(socket.id)
                    sel_sockets_info.append(socket)

            elif isinstance(item, QDMGraphicsEdge):
                sel_edges.append(item.edge)


        #debug
        if DEBUG:
            print("   NODES:\n    {}".format(sel_nodes))
            print("   Edges:\n    {}".format(sel_edges))
            print("   Sockets:\n    {}".format(sel_sockets))

        # remove all edges which not connected in list
        edges_to_remove = []
        #print(sel_sockets)
        for edge in sel_edges:
            #print("\n{}\n".format(edge.start_socket.id))
            #print("\n{}\n".format(sel_sockets))
            #print("\n{}\n".format(edge.end_socket.id))
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                if DEBUG: print("edge is ok")
                pass
            else:
                if DEBUG: print("edge {} not connected at both sides ".format(edge))
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            sel_edges.remove(edge)

        # make final list of edges
        edges_final = []
        for edge in sel_edges:
            #print("\n\nsss{}sss\n\n".format(edge))
            #print("\n\nsss{}sss\n\n".format(edge.serialize()))
            edges_final.append(edge.serialize())

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final)

        ])
        # if cut (and delete) remove selected items
        if delete:
            self.scene.getView().deleteSelected()
            #store history
            self.scene.history.storeHistory("Cut out elements from scene", setModified=True)
        return data

    def deserializeFromClipboard(self, data):

        hashmap = {}
        #calc mouse pointer - scene position

        # calc selected obj bbox and center
        view = self.scene.getView()
        mouse_scene_pos = view.last_scene_mouse_position
        #calc offset of newly creating nodes
        minx, maxx, miny,maxy = self.scene.scene_width,-self.scene.scene_width,self.scene.scene_height,-self.scene.scene_height
        for node_data in data['nodes']:
            x,y = node_data['pos_x'], node_data['pos_y']
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxy) / 2
        center = view.mapToScene(view.rect().center())


        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y
        # create each node
        for node_data in data['nodes']:
            new_node = self.scene.getNodeClassFormData(node_data)(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            # readjust the new node`s position
            pos = new_node.pos
            new_node.setPos(pos.x() + offset_x, pos.y() + offset_y)
        # create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)
        #store history

        self.scene.history.storeHistory("Pasted elements in scene", setModified=True)