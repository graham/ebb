import trees

### Base Operation.

class Operation(object):
    pass

class CompoundOperation(Operation):
    def __init__(self, operations):
        self.operations = operations

    def pack(self):
        return ['CompoundOperation', [i.pack() for i in self.operations]]

    def apply(self, node):
        cur = node
        revs = []
        for i in self.operations:
            cur, reverse = i.apply(cur)
            revs.append(reverse)
        return cur, CompoundOperation(revs)

### Number Operations.

class NumberIncrementOperation(Operation):
    def __init__(self, amount):
        self.amount = amount
        
    def pack(self):
        return ['NumberIncrementOperation', self.amount]

    def apply(self, node):
        new = node.proto(node.obj_repr() + self.amount)
        reverse = NumberIncrementOperation(self.amount * (-1))
        return new, reverse

### String Operations.

class StringInsertOperation(Operation):
    def __init__(self, index, text):
        self.index = index
        self.text = text

    def pack(self):
        return ['StringInsertOperation', self.index, self.text]
        
    def apply(self, node):
        node_value = node.obj_repr()
        new = node.proto(node_value[:self.index] + self.text + node_value[self.index:])
        reverse = StringDeleteOperation(self.index, len(self.text))
        return new, reverse

class StringDeleteOperation(Operation):
    def __init__(self, index, length):
        self.index = index
        self.length = length

    def pack(self):
        return ['StringDeleteOperation', self.index, self.length]

    def apply(self, node):
        node_value = node.obj_repr()
        new = node.proto(node_value[:self.index] + node_value[self.index + self.length:])
        reverse = StringInsertOperation(self.index, node_value[self.index:self.index+self.length])
        return new, reverse

class StringSetOperation(Operation):
    def __init__(self, value):
        self.value = value

    def pack(self):
        return ['StringSetOperation', self.value]

    def apply(self, node):
        new = node.proto(self.value)
        reverse = StringSetOperation(node.obj_repr())
        return new, reverse

### Boolean operations.

class BooleanSetOperation(Operation):
    def __init__(self, value):
        self.value = value

    def pack(self):
        return ["BooleanSetOperation", self.value]

    def apply(self, node):
        new = node.proto(self.value)
        reverse = BooleanSetOperation(not self.value)
        return new, reverse

### List operations.

class ListInsertOperation(Operation):
    def __init__(self, index, value):
        self.index = index
        self.value = value

    def pack(self):
        return ["ListInsertOperation", self.index, self.value]

    def apply(self, node):
        new = node.proto(children=node.children[:self.index] + self.value + node.children[self.index:])
        reverse = ListDeleteOperation(self.index, len(self.value))
        return new, reverse
        
class ListDeleteOperation(Operation):
    def __init__(self, index, length):
        self.index = index
        self.length = length

    def pack(self):
        return ["ListDeleteOperation", self.index, self.length]

    def apply(self, node):
        new = node.proto(children=node.children[:self.index] + node.children[self.index + self.length:])
        reverse = ListInsertOperation(self.index, node.children[self.index:self.index+self.length])
        return new, reverse

class ListSetIndexOperation(Operation):
    def __init__(self, index, value):
        self.index = index
        self.value = value

    def pack(self):
        return ["ListSetIndexOperation", self.index, self.value]

    def apply(self, node):
        old = node.children[self.index]
        new_node = node.proto()
        new_node.children = []

        for index, item in enumerate(node.children):
            if index == self.index:
                new_node.children.append(self.value)
            else:
                new_node.children.append(item)

        reverse = ListSetIndexOperation(self.index, old)
        return new_node, reverse

class ListApplyIndexOperation(Operation):
    def __init__(self, index, operation):
        self.index = index
        self.operation = operation

    def pack(self):
        return ["ListApplyIndexOperation", self.index, self.operation.pack()]

    def apply(self, node):
        new, reverse = self.operation.apply(node.children[self.index])
        reverse_op = ListApplyIndexOperation(self.index, reverse)

        new_node = node.proto()
        new_node.children = []
        
        for index, item in enumerate(node.children):
            if index == self.index:
                new_node.children.append(new)
            else:
                new_node.children.append(item)

        return new_node, reverse_op

### Dictionary Operations.
### This is tricky.
class DictKeyApplyOperation(Operation):
    def __init__(self, key, operation):
        self.key = key
        self.operation = operation

    def pack(self):
        return ["DictKeyApplyOperation", self.key, self.operation.pack()]

    def apply(self, node):
        child = node.get_path(self.key)
        new, reverse = self.operation.apply(child)

        new_node = node.proto(node.value)
        for index, item in enumerate(node.children):
            new_node.children.append(item)
        new_node.set_path(self.key, new)

        reverse_op = DictKeyApplyOperation(self.key, reverse)
        return new_node, reverse_op
        
### Things that still need to be done.

class MoveBookmarkOperation(Operation): 
    pass
class CopyBookmarkOperation(Operation):
    pass
class PruneBookmarkOperation(Operation):
    pass

op_lookup = {
    'CompoundOperation':CompoundOperation,
    'NumberIncrementOperation':NumberIncrementOperation,
    'StringInsertOperation':StringInsertOperation,
    'StringDeleteOperation':StringDeleteOperation,
    'StringSetOperation':StringSetOperation,
    'BooleanSetOperation':BooleanSetOperation,
    'ListInsertOperation':ListInsertOperation,
    'ListDeleteOperation':ListDeleteOperation,
    'ListSetIndexOperation':ListSetIndexOperation,
    'ListApplyIndexOperation':ListApplyIndexOperation,
    'DictKeyApplyOperation':DictKeyApplyOperation
}

def unpack(args):
    klass = op_lookup[args[0]]
    return klass(*args[1:])
