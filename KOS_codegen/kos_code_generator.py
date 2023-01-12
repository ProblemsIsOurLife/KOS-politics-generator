import os

from nodeeditor.utils import pp, dumpException

DEBUG=True

class ExportKosCode():
    def __init__(self, widget):
        self.widget = widget
        self.nodes, self.edges = [], []
        self.project_name = os.path.basename(self.widget.filename)
        self.project_name=self.project_name.replace(".json", "")
        self.resourses_path = os.path.join(os.path.dirname(__file__),"export_files",self.project_name,"resourses")
        self.security_path = os.path.join(os.path.dirname(__file__), "export_files",self.project_name, "einit","src")

        self.export()

    def export(self):
        self.createDir()
        self.load_Data()

        if self.check():
            return False
        else:
            return True

    def check(self):
        if [char for char in self.project_name[0] if char == '_']:
            #print(True)
            return True
        else:
            #print(False)
            return False
        for node in self.nodes:
            if [char for char in node if char == '_']:
                #print(True)
                return True
            else:
                #print(False)
                return False
    def load_Data(self):
        #for item in self.scene.edges:
       #     print("sockets:{} and {}\n".format(item._start_socket, item._end_socket))
       # for item in self.scene.nodes:
        #    for socket in item.inputs:
        #        print("node:{}\nsocket & type: {} and {}".format(item, socket, socket))
        serialized = self.widget.scene.serialize()
        hashmap = {}

        for node in serialized['nodes']:
            #if node['id'] not in self.nodes:
                self.nodes.append(node)
            #print(new_node.id)
           # print(new_node.title)
            #print(new_node['content']['endpoint_data'])
           # print(new_node.outputs)

        if 'edges' in serialized:
            for edge in serialized['edges']:
                #edges.append(edge)
                #new_edge = Edge(self.widget.scene.grScene)
                #new_edge.deserialize(edge, hashmap, restore_id=True)

                id = edge['id']
                end_socket = edge['end']
                start_socket = edge['start']
                if [id,start_socket,end_socket] not in self.edges:
                    self.edges.append([id,start_socket,end_socket])
                #print(id)
                #print(start_socket, end_socket)
            #print(self.edges)

        #pp(nodes)
        #pp(edges)
        #print("nodes:{}\nedges:{}".format(nodes,edges))

        self.export_Entities(self.nodes)
        #self.export_Components(self.nodes)
        self.export_Security(self.nodes, self.edges)
    def createDir(self):
        try:
            os.makedirs(self.resourses_path,exist_ok=True)
            os.makedirs(self.security_path, exist_ok=True)
        except Exception as e:
            dumpException(e)

    def export_Entities(self, nodes):
        all_nodes = []

        #entity name
        #"{}.{}".format(self.project_name,node.title.replace(" ", ""))

        for node in nodes:
            if node['title'] not in all_nodes and node['op_code'] == 2:
                all_nodes.append(node['title'])
        have_endpoint = False
        project_name = self.project_name.replace(" ", "")
        if project_name[:1] == '_':
            project_name = project_name[:1].replace('_', '') + project_name[1:]
        endpoint_string = ""
        methods_string = ""
        finded_endpoints = []
        writed_endpoints = []
        endpoint_founded = False
        for name in all_nodes:
            temp_name = name
            temp_name = temp_name[:1].upper() + temp_name[1:]
            filename = "{}\{}.edl".format(self.resourses_path, temp_name)
            for node in nodes:
                if node['title'] == name:
                    if node['content']['endpoint_data'] != '' and node['content']['endpoint_data'] not in finded_endpoints:
                        finded_endpoints.append(node['content']['endpoint_data'])
            if len(finded_endpoints) != 0:
                for endpoint in finded_endpoints:
                    for node in nodes:
                        if node['title'] == name:
                            if node['content']['endpoint_data'] != '' and node['content']['endpoint_data'] == endpoint:
                                endpoint_name = node['content']['endpoint_data']
                                endpoint_name = endpoint_name[:1].lower() + endpoint_name[1:]
                                if node['content']['endpoint_data'] not in writed_endpoints:
                                    endpoint_string += "\n\t{} : {}.{}".format(endpoint_name, project_name,node['content']['endpoint_data'])
                                    writed_endpoints.append(node['content']['endpoint_data'])
                                if node['content']['method_data'] != '':
                                    temp_method_name = node['content']['endpoint_data'].replace("_", "")
                                    temp_method_name = temp_method_name.replace(" ", "")
                                    temp_method_name = temp_method_name[:1].upper() + temp_method_name[1:]
                                    methods_string+="\n\t{};".format(node['content']['method_data'])

                    if methods_string != '':
                        self.export_Interfaces(temp_method_name, methods_string)
                    methods_string = ''
                    temp_method_name = ''
                    string = ''
                with open(filename, "w") as file:
                    string = "entity {}.{}".format(project_name, name)
                    if endpoint_string!='':
                        string += "\ninterfaces\n{{{}\n}}".format(endpoint_string)
                    file.write(string)
                    print("saving to {} was successfull".format(filename))
                    endpoint_name = ''

                endpoint_string = ""
            else:
                with open(filename, "w") as file:
                    string = "entity {}.{}".format(project_name, name)
                    print("saving to {} was successfull".format(filename))
                    string = ''


    # def export_Components(self, nodes):
    #     components_title = []
    #     print(nodes)
    #     for node in nodes:
    #         if node['content']['endpoint_data'] not in components_title and node['op_code'] == 2:
    #             components_title.append(node['content']['endpoint_data'])
    #     print(components_title)


    def export_Interfaces(self, name, data):
        project_name = self.project_name.replace(" ", "")
        if project_name[:1] == '_':
            project_name = project_name[:1].replace('_', '') + project_name[1:]
        filename = "{}\{}.idl".format(self.resourses_path, name)
        string = "package {}.{}\n\ninterface\n{{{}\n}}".format(project_name, name, data)
        with open(filename, "w") as file:
            file.write(string)
            print("saving to {} was successfull".format(filename))



    def export_Security(self, nodes, edges):
        base_export = "execute: kl.core.Execute\nuse nk.base._\n\nuse EDL Einit\nuse EDL kl.core.Core\n"
        entity_names = []
        project_name = self.project_name.replace(" ", "")
        if project_name[:1] == '_':
            project_name = project_name[:1].replace('_','') + project_name[1:]
        all_granted_nodes_sockets = []
        for node in nodes:
            if node['title'] not in entity_names and node['op_code'] == 2:
                entity_names.append(node['title'])
        for name in entity_names:
            name = name[:1].upper() + name[1:]
            base_export += "\nuse EDL {}.{}".format(project_name, name)
        #base_export += "\n\nexecute\n{\n\tgrant ();\n}\n\n"
        for node in nodes:
            if node['op_code'] == 1:
                all_granted_nodes_sockets.append(node['outputs'][0]['id'])
        tempedges = []
        to_remove_from_temp = False
        for edge in edges:
            tempedges.append(edge)
        for edge in tempedges:
            for socket in all_granted_nodes_sockets:
                if edge[1] == socket:
                    to_remove_from_temp = True
                    for node in nodes:
                        if node['op_code'] == 2:
                            if edge[2] == node['inputs'][0]['id']:
                                if node['content']['assert_data'] == '':
                                    if node['content']['endpoint_data'] == '':
                                        base_export += "\nresponse dst={}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                            project_name,node['title'])
                                    else:
                                        if node['content']['method_data'] == '':
                                            base_export += "\nresponse dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                project_name,node['title'], project_name,node['content']['endpoint_data'])
                                        else:
                                            base_export += "\nresponse dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                node['content']['method_data'])
                                else:
                                    if node['content']['endpoint_data'] == '':
                                        base_export += "\nresponse dst = {}.{} \n{{\n\tassert({})\n}}\n\n".format(
                                            project_name,node['title'], node['content']['assert_data'])
                                    else:
                                        if node['content']['method_data'] == '':
                                            base_export += "\nresponse dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                node['content']['assert_data'])
                                        else:
                                            base_export += "\nresponse dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                node['content']['method_data'], node['content']['assert_data'])

                            for outputs in node['outputs']:
                                if edge[2] == outputs['id'] and outputs['type'] == 2:
                                    if node['content']['assert_data'] == '':
                                        base_export += "\nrequest src = {}.{}\n{{\n\tgrant()\n}}\n\n".format(project_name,node['title'])
                                        base_export += "\nresponse src = {}.{}\n{{\n\tgrant()\n}}\n\n".format(project_name,node['title'])
                                    else:
                                        base_export += "\nrequest src = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                            project_name,node['title'],node['content']['assert_data'])
                                        base_export += "\nresponse src = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                            project_name,node['title'],node['content']['assert_data'])
                                if edge[2] == outputs['id'] and outputs['type'] == 3:
                                    if node['content']['assert_data'] == '':
                                        if node['content']['endpoint_data'] == '':
                                            base_export += "\nrequest dst = {}.{}\n{{\n\tgrant()\n}}\n\n".format(project_name,node['title'])
                                        else:
                                            if node['content']['method_data'] == '':
                                                base_export += "\nrequest dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                    project_name,node['title'], project_name,node['content']['endpoint_data'])
                                            else:
                                                base_export += "\nrequest dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                    project_name,node['title'], project_name,node['content']['endpoint_data'],node['content']['method_data'])
                                    else:
                                        if node['content']['endpoint_data'] == '':
                                            base_export += "\nrequest dst = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                project_name,node['title'],node['content']['assert_data'])
                                        else:
                                            if node['content']['method_data'] == '':
                                                base_export += "\nrequest dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                    project_name,node['title'],project_name, node['content']['endpoint_data'],node['content']['assert_data'])
                                            else:
                                                base_export += "\nrequest dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                    project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                    node['content']['method_data'],node['content']['assert_data'])
                if edge[2] == socket:
                    to_remove_from_temp = True
                    for node in nodes:
                        if node['op_code'] == 2:
                            if edge[2] == node['inputs'][0]['id']:
                                base_export += "\nresponse src = {}.{}\n{{\n\tgrant()\n}}\n\n".format(project_name,node['title'])

                            for node in nodes:
                                if node['op_code'] == 2:
                                    if edge[1] == node['inputs']['id']:
                                        if node['content']['assert_data'] == '':
                                            base_export += "\nresponse src = {}.{} \n{{\n\tgrant()\n}}\n\n".format(
                                                project_name,node['title'])
                                        else:
                                            base_export += "\nresponse src = {}.{} \n{{\n\tassert({})\n}}\n\n".format(node['title'],
                                                project_name,node['content']['assert_data'])

                                    for outputs in node['outputs']:
                                        if edge[1] == outputs['id'] and outputs['type'] == 2:
                                            if node['content']['assert_data'] == '':
                                                base_export += "\nrequest src = {}.{} \n{{\n\tgrant()\n}}\n\n".format(
                                                    project_name,node['title'])
                                                base_export += "\nresponse src = {}.{} \n{{\n\tgrant()\n}}\n\n".format(
                                                    project_name,node['title'])
                                            else:
                                                base_export += "\nrequest src = {}.{} \n{{\n\tassert({})\n}}\n\n".format(project_name,node['title'],
                                                    node['content']['assert_data'])
                                                base_export += "\nresponse src = {}.{} \n{{\n\tassert({})\n}}\n\n".format(project_name,node['title'],
                                                    node['content']['assert_data'])
                                        if edge[1] == outputs['id'] and outputs['type'] == 3:
                                            if node['content']['assert_data'] == '':
                                                if node['content']['endpoint_data'] == '':
                                                    base_export += "\nresponse dst = {}.{} \n{{\n\tgrant()\n}}\n\n".format(
                                                        project_name,node['title'])
                                                else:
                                                    if node['content']['method_data'] == '':
                                                        base_export += "\nresponse dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                            project_name,node['title'], project_name,node['content']['endpoint_data'])
                                                    else:
                                                        base_export += "\nresponse dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                            project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                            node['content']['method_data'])
                                            else:
                                                if node['content']['endpoint_data'] == '':
                                                    base_export += "\nresponse dst = {}.{} \n{{\n\tassert({})\n}}\n\n".format(
                                                        project_name,node['title'], node['content']['assert_data'])
                                                else:
                                                    if node['content']['method_data'] == '':
                                                        base_export += "\nresponse dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                            project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                            node['content']['assert_data'])
                                                    else:
                                                        base_export += "\nresponse dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                            project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                            node['content']['method_data'], node['content']['assert_data'])
            if to_remove_from_temp:
                tempedges.remove(edge)
            to_remove_from_temp = False
        for edge in tempedges:
            for node in nodes:
                if node['op_code'] == 2:
                    for node_socket in node['outputs']:
                        if edge[1] == node_socket['id'] and node_socket['type'] == 2:
                            for temp_node in nodes:
                                if temp_node != node:
                                    if edge[2] == temp_node['inputs'][0]['id']:
                                        if temp_node['content']['assert_data'] == '':
                                            if temp_node['content']['endpoint_data'] == '':
                                                base_export += "\nresponse src = {}.{},\ndst = {}.{} \n{{\n\tgrant()\n}}\n\n".format(
                                                    project_name,temp_node['title'],project_name,node['title'])
                                            else:
                                                if temp_node['content']['method_data'] == '':
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'])
                                                else:
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'],
                                                        temp_node['content']['method_data'])
                                        else:
                                            if temp_node['content']['endpoint_data'] == '':
                                                base_export += "\nresponse src = {}.{}, dst = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                    project_name,temp_node['title'],project_name,node['title'], temp_node['content']['assert_data'])
                                            else:
                                                if temp_node['content']['method_data'] == '':
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'],
                                                        temp_node['content']['assert_data'])
                                                else:
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'],
                                                        temp_node['content']['method_data'], temp_node['content']['assert_data'])
                                    else:
                                        for temp_socket in temp_node['outputs']:############################
                                            if temp_socket['id'] == edge[2] and temp_socket['type'] == 3:
                                                if node['content']['assert_data'] == '':
                                                    if node['content']['endpoint_data'] == '':
                                                        base_export += "\nrequest src = {}.{}, dst = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                            project_name,temp_node['title'],project_name,node['title'])
                                                    else:
                                                        if node['content']['method_data'] == '':
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'])
                                                        else:
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                                node['content']['method_data'])
                                                else:
                                                    if node['content']['endpoint_data'] == '':
                                                        base_export += "\nrequest src = {}.{}, dst = {}.{} \n{{\n\tassert({})\n}}\n\n".format(
                                                            project_name,temp_node['title'],project_name,node['title'], node['content']['assert_data'])
                                                    else:
                                                        if node['content']['method_data'] == '':
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                                node['content']['assert_data'])
                                                        else:
                                                            base_export += "\nrequest src = {}, dst = {}, interface = {}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                                node['title'],node['title'], node['content']['endpoint_data'],
                                                                node['content']['method_data'],
                                                                node['content']['assert_data'])
                        if  edge[2] == node_socket['id'] and node_socket['type'] == 2:
                            for temp_node in nodes:
                                if temp_node != node:
                                    if edge[1] == temp_node['inputs'][0]['id']:
                                        if temp_node['content']['assert_data'] == '':
                                            if temp_node['content']['endpoint_data'] == '':
                                                base_export += "\nresponse src = {}.{}, dst = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                    project_name,temp_node['title'],project_name,node['title'])
                                            else:
                                                if temp_node['content']['method_data'] == '':
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'])
                                                else:
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'],
                                                        temp_node['content']['method_data'])
                                        else:
                                            if temp_node['content']['endpoint_data'] == '':
                                                base_export += "\nresponse src = {}.{}, dst = {}.{} \n{{\n\tassert({})\n}}\n\n".format(
                                                    project_name,temp_node['title'],project_name,node['title'], temp_node['content']['assert_data'])
                                            else:
                                                if temp_node['content']['method_data'] == '':
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'], project_name,temp_node['content']['endpoint_data'],
                                                        temp_node['content']['assert_data'])
                                                else:
                                                    base_export += "\nresponse src = {}.{}, dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                        project_name,temp_node['title'],project_name,node['title'],project_name, temp_node['content']['endpoint_data'],
                                                        temp_node['content']['method_data'], temp_node['content']['assert_data'])
                                    else:
                                        for temp_socket in temp_node['outputs']:
                                            if temp_socket['id'] == edge[1] and temp_socket['type'] == 3:
                                                if node['content']['assert_data'] == '':
                                                    if node['content']['endpoint_data'] == '':
                                                        base_export += "\nrequest src = {}.{}, dst = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                            project_name,temp_node['title'],project_name,node['title'])
                                                    else:
                                                        if node['content']['method_data'] == '':
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tgrant()\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'])
                                                        else:
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{},method = {} \n{{\n\tgrant()\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                                node['content']['method_data'])
                                                else:
                                                    if node['content']['endpoint_data'] == '':
                                                        base_export += "\nrequest src = {}.{}, dst = {}.{} \n{{\n\tassert({})\n}}\n\n".format(
                                                            project_name,temp_node['title'],project_name,node['title'], node['content']['assert_data'])
                                                    else:
                                                        if node['content']['method_data'] == '':
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{}\n{{\n\tassert({})\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                                node['content']['assert_data'])
                                                        else:
                                                            base_export += "\nrequest src = {}.{}, dst = {}.{}, interface = {}.{}, method = {} \n{{\n\tassert({})\n}}\n\n".format(
                                                                project_name,temp_node['title'],project_name,node['title'], project_name,node['content']['endpoint_data'],
                                                                node['content']['method_data'],
                                                                node['content']['assert_data'])
        filename = "{}\security.cfg".format(self.security_path)
        with open(filename, "w") as file:
            file.write(base_export)
            print("saving to {} was successfull".format(filename))

