import trees
import uuid
import json

def safe_bound(x):
    if x > 0:
        return x
    else:
        return 0


### Base Operation.
class Operation(object):
    for_type = '*'

    def __init__(self):
        self._id = str(uuid.uuid4())
        #for the new way of thinking
        self.target_revision = None

    def __repr__(self):
        return "<Op: %s>" % self.pack()

    @classmethod
    def unpack(cls, args):
        klass = op_lookup[args[0]]
        if len(args) > 3 and type(args[3]) == list:
            args[3] = map(lambda x: trees.Node.unpack(x), args[3])

        k = klass(*args[2:])
        k._id = args[1]
        return k

    def clone(self):
        # This is a all around bad method, but frankly, I want to ensure that
        # if you get an object it can't change out from under you, so this is
        # one way to get it done until I come up with a cleaner way.
        return Operation.unpack(self.pack())

    ###### Now it gets fun, this should eventually be split out into classes or
    ###### some sort of lookup table so that the user could feasibly define
    ###### their own, although, that also seems like a bad idea.
    def handle_mutate(self, root, tpath, oplist):
        new_list = []
        for row in oplist:
            new_row = row

            if tpath and tpath != row[1]:
                if all([i == j for i, j in zip(tpath, row[1])]):
                    new_row = self.handle_mutate_with_path(row, tpath)
                new_list.append(new_row)
            else:
                if self.for_type == 'dict':
                    if self.source_path == row[1]:
                        new_row = self.handle_mutate_without_path(row, tpath)
                        root = root.get_path(new_row[1])
                elif self.for_type in ('list', 'string'):
                    if self.index > row[2].index:
                        ## this means that modifications don't affect
                        ## this op.
                        pass
                    else:
                        new_row = self.handle_mutate_without_path(row, tpath)
                else:
                    raise Exception('unsupported type')

                newroot, newrev = new_row[2].apply(root)
                new_list.append([new_row[0], new_row[1], new_row[2], newrev])
                root = newroot

        return new_list

    def handle_mutate_with_path(self, row, tpath):
        if self.for_type == 'string':
            return self.handle_mutate_with_path_string(row, tpath)
        elif self.for_type == 'list':
            return self.handle_mutate_with_path_list(row, tpath)
        elif self.for_type == 'dict':
            return self.handle_mutate_with_path_dict(row, tpath)
        else:
            return row

    def handle_mutate_with_path_string(self, row, tpath):
        p = row[2].clone()
        if type(self) == StringInsertOperation:
            p.index = safe_bound(p.index + len(self.text))
        elif type(self) == StringDeleteOperation:
            p.index = safe_bound(p.index - self.length)
        return [row[0], row[1], p, row[3]]

    def handle_mutate_with_path_list(self, row, tpath):
        path = row[1]
        if type(self) == ListInsertOperation:
            path[len(tpath)] = safe_bound(path[len(tpath)] + len(self.value))
        elif type(self) == ListDeleteOperation:
            path[len(tpath)] = safe_bound(path[len(tpath)] - self.length)

        return [row[0], path, row[2], row[3]]

    def handle_mutate_without_path(self, row, tpath):
        if self.for_type == 'string':
            return self.handle_mutate_without_path_string(row, tpath)
        elif self.for_type == 'list':
            return self.handle_mutate_without_path_list(row, tpath)
        elif self.for_type == 'dict':
            return self.handle_mutate_without_path_dict(row, tpath)
        else:
            return row

    def handle_mutate_without_path_dict(self, row, tpath):
        return [row[0], self.target_path, row[2], row[3]]
        
    def handle_mutate_without_path_string(self, row, tpath):
        p = row[2].clone()

        if type(self) == StringInsertOperation:
            p.index = safe_bound(p.index + len(self.text))
        elif type(self) == StringDeleteOperation:
            p.index = safe_bound(p.index - self.length)

        return [row[0], row[1], p, row[3]]

    def handle_mutate_without_path_list(self, row, tpath):
        p = row[2].clone()
        if type(self) == ListInsertOperation:
            p.index = safe_bound(p.index + len(self.value))
        elif type(self) == ListDeleteOperation:
            p.index = safe_bound(p.index - self.length)
        return [row[0], row[1], p, row[3]]
    ### End of GOT type conflict resolution.

    ### Begin Pavelian History Maintenence.
    def cross_merge(self, previous_transform):
        assert self.for_type == previous_transform.for_type

        if self.for_type in trees.APPLY_TYPES:
            return self
        elif self.for_type in (trees.TYPES['string'], trees.TYPES['list']):
            pass
    ### End Pavelian History Maintenence.


### Basic Set Operation
class SetOperation(Operation):
    for_type = '*'

    def __init__(self, value):
        Operation.__init__(self)
        self.value = value

    def pack(self):
        return ['SetOperation', self._id, self.value]

    def apply(self, node):
        new = trees.Node.from_obj(self.value)
        reverse = SetOperation(node.obj_repr())
        return new, reverse


### Number Operations.
class NumberIncrementOperation(Operation):
    for_type = 'number'

    def __init__(self, amount):
        Operation.__init__(self)
        self.amount = amount

    def pack(self):
        return ['NumberIncrementOperation', self._id, self.amount]

    def apply(self, node):
        new = node.clone()
        new.set_value(node.obj_repr() + self.amount)
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
        new = node.clone()
        new.set_value(nv)

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
        new = node.clone()
        new.set_value(node_value[:self.index] +
                      node_value[self.index + self.length:])

        reverse = StringInsertOperation(
            self.index, node_value[self.index:self.index + self.length])
        return new, reverse


class StringSetOperation(Operation):
    for_type = 'string'

    def __init__(self, value):
        Operation.__init__(self)
        self.value = value

    def pack(self):
        return ['StringSetOperation', self._id, self.value]

    def apply(self, node):
        new = node.clone()
        new.set_value(self.value)
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
        new = node.clone()
        new.set_value(self.value)

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
        return ["ListInsertOperation", self._id, self.index, [i.pack() for i in self.value]]

    def apply(self, node):
        new = node.clone()
        new.children = new.children[:self.index] + self.value + new.children[self.index:]
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
        new = node.clone()
        reverse = ListInsertOperation(
            self.index, new.children[self.index:self.index + self.length])
        new.children = new.children[:self.index] + new.children[self.index + self.length:]
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
        new_node = node.clone()
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

        new_node = node.clone()
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

        new_node = node.clone()
        new_node.set_path(self.key, new)

        reverse_op = DictKeyApplyOperation(self.key, reverse)
        return new_node, reverse_op

## SUP
class MovePathOperation(Operation):
    for_type = 'dict'

    def __init__(self, source_path, target_path):
        Operation.__init__(self)
        self.source_path = source_path
        self.target_path = target_path

    def pack(self):
        return ['MovePathOperation', self._id, self.source_path, self.target_path]

    def apply(self, node):
        new = node.clone()
        value = new.get_path(self.source_path)
        new.remove_path(self.source_path)
        new.set_path(self.target_path, value)

        reverse = MovePathOperation(self.target_path, self.source_path)
        return new, reverse


#sets
class SetAddOperation(Operation):
    for_type = 'set'

    def __init__(self, value):
        Operation.__init__(self)
        self.value = value

    def pack(self):
        return ["SetAddOperation", self._id, self.value]

    def apply(self, node):
        pass


class SetRemoveOperation(Operation):
    for_type = 'set'

    def __init__(self, value):
        Operation.__init__(self)
        self.value = value

    def pack(self):
        return ["SetRemoveOperation", self._id, self.value]

    def apply(self, node):
        pass


# zsets
class ScoredSetAddOperation(Operation):
    pass


class ScoredSetApplyOperation(Operation):
    pass


class ScoredSetDropOperation(Operation):
    pass


op_lookup = {
    'NumberIncrementOperation': NumberIncrementOperation,
    'StringInsertOperation': StringInsertOperation,
    'StringDeleteOperation': StringDeleteOperation,
    'StringSetOperation': StringSetOperation,
    'BooleanSetOperation': BooleanSetOperation,
    'ListInsertOperation': ListInsertOperation,
    'ListDeleteOperation': ListDeleteOperation,
    'ListSetIndexOperation': ListSetIndexOperation,
    'ListApplyIndexOperation': ListApplyIndexOperation,
    'DictKeyApplyOperation': DictKeyApplyOperation
}

