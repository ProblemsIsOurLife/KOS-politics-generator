LISTBOX_MIMETYPE = "application/x-item"
OP_NODE_ALL_GRANTED = 1
OP_NODE_BASE_WIDGET = 2


KOS_NODES = {

}


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OPCodeNotRegistered(ConfException): pass

def register_node_now(op_code, class_reference):
    if op_code is KOS_NODES:
        raise InvalidNodeRegistration("Duplicate node registration of {} - already exists - {}".format(op_code, KOS_NODES[op_code]))
    KOS_NODES[op_code] = class_reference
    #KOS_NODES.append(op_code: class_reference)
def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator
def get_class_from_opcode(op_code):
    if op_code not in KOS_NODES:
        raise OPCodeNotRegistered("OpCode {} is not registered".format(op_code))
    return KOS_NODES[op_code]