import trees
import uuid


def safe_bound(x):
    if x > 0:
        return x
    else:
        return 0


### Base Operation.
class Operation(object):
    def __init__(self):
        self._id = str(uuid.uuid4())

    def __repr__(self):
        return "<Op: %s>" % self.pack()

    def clone(self):
        return unpack(self.pack())

    def path_hit(self, target_path, path):
        i = all([i == j for i, j in zip(target_path, path)])
        return target_path and (path != target_path) and i


### Number Operations.
class NumberIncrementOperation(Operation):
    for_type = 'number'

    def __init__(self, amount):
        Operation.__init__(self)
        self.amount = amount

    def pack(self):
        return ['NumberIncrementOperation', self._id, self.amount]

    def apply(self, node):
        new = node.proto(node.obj_repr() + self.amount)
        reverse = NumberIncrementOperation(self.amount * (-1))
        return new, reverse


### String Operations.
class StringInsertOperation(Operation):
    for_type = 'string'

    def __init__(self, index, text):
        Operation.__init__(self)
        self.index = index
        self.text = text

    def pack(self):
        return ['StringInsertOperation', self._id, self.index, self.text]

    def apply(self, node):
        node_value = str(node.obj_repr())
        nv = node_value[:self.index] + self.text + node_value[self.index:]
        new = node.proto(nv)

        reverse = StringDeleteOperation(self.index, len(self.text))
        return new, reverse


class StringDeleteOperation(Operation):
    for_type = 'string'

    def __init__(self, index, length):
        Operation.__init__(self)
        self.index = index
        self.length = length

    def pack(self):
        return ['StringDeleteOperation', self._id, self.index, self.length]

    def apply(self, node):
        node_value = str(node.obj_repr())
        new = node.proto(node_value[:self.index] + node_value[self.index + self.length:])
        reverse = StringInsertOperation(self.index, node_value[self.index:self.index+self.length])
        return new, reverse

class StringSetOperation(Operation):
    for_type = 'string'
    def __init__(self, value):
        Operation.__init__(self)
        self.value = value

    def pack(self):
        return ['StringSetOperation', self._id, self.value]

    def apply(self, node):
        new = node.proto(self.value)
        reverse = StringSetOperation(node.obj_repr())
        return new, reverse

### Boolean operations.

class BooleanSetOperation(Operation):
    for_type = 'boolean'
    def __init__(self, value):
        Operation.__init__(self)
        self.value = value

    def pack(self):
        return ["BooleanSetOperation", self._id, self.value]

    def apply(self, node):
        new = node.proto(self.value)
        reverse = BooleanSetOperation(not self.value)
        return new, reverse

### List operations.

class ListInsertOperation(Operation):
    for_type = 'list'
    def __init__(self, index, value):
        Operation.__init__(self)
        self.index = index
        self.value = value

    def pack(self):
        return ["ListInsertOperation", self._id, self.index, self.value]

    def apply(self, node):
        new = node.proto(children=node.children[:self.index] + self.value + node.children[self.index:])
        reverse = ListDeleteOperation(self.index, len(self.value))
        return new, reverse

class ListDeleteOperation(Operation):
    for_type = 'list'
    def __init__(self, index, length):
        Operation.__init__(self)
        self.index = index
        self.length = length

    def pack(self):
        return ["ListDeleteOperation", self._id, self.index, self.length]

    def apply(self, node):
        new = node.proto(children=node.children[:self.index] + node.children[self.index + self.length:])
        reverse = ListInsertOperation(self.index, node.children[self.index:self.index+self.length])
        return new, reverse

class ListSetIndexOperation(Operation):
    for_type = 'list'
    def __init__(self, index, value):
        Operation.__init__(self)
        self.index = index
        self.value = value

    def pack(self):
        return ["ListSetIndexOperation", self._id, self.index, self.value]

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
    for_type = 'list'
    def __init__(self, index, operation):
        Operation.__init__(self)
        self.index = index
        self.operation = operation

    def pack(self):
        return ["ListApplyIndexOperation", self._id, self.index, self.operation.pack()]

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
    for_type = 'dict'
    def __init__(self, key, operation):
        Operation.__init__(self)
        self.key = key
        self.operation = operation

    def pack(self):
        return ["DictKeyApplyOperation", self._id, self.key, self.operation.pack()]

    def apply(self, node):
        child = node.get_path(self.key)
        new, reverse = self.operation.apply(child)

        new_node = node.proto(node.value)
        for index, item in enumerate(node.children):
            new_node.children.append(item)
        new_node.set_path(self.key, new)

        reverse_op = DictKeyApplyOperation(self.key, reverse)
        return new_node, reverse_op

## Work to do.
class DictMoveKeyOperation(Operation):
    pass
class DictDropKeyOperation(Operation):
    pass

# sets
class SetAddOperation(Operation):
    pass
class SetRemoveOperation(Operation):
    pass

# zsets
class ScoredSetAddOperation(Operation):
    pass
class ScoredSetApplyOperation(Operation):
    pass
class ScoredSetDropOperation(Operation):
    pass


op_lookup = {
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
    k = klass(*args[2:])
    k._id = args[1]
    return k
