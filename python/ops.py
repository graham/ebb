import trees

### Base Operation.

class Operation(object):
    pass

### Number Operations.

class NumberIncrementOperation(Operation):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, node):
        new = node.proto(node.obj_repr() + self.amount)
        reverse = NumberIncrementOperation(self.amount * (-1))
        return new, reverse

### String Operations.

class StringInsertOperation(Operation):
    def __init__(self, index, text):
        self.index = index
        self.text = text

    def apply(self, node):
        node_value = node.obj_repr()
        new = node.proto(node_value[:self.index] + self.text + node_value[self.index:])
        reverse = StringDeleteOperation(self.index, len(self.text))
        return new, reverse

class StringDeleteOperation(Operation):
    def __init__(self, index, length):
        self.index = index
        self.length = length

    def apply(self, node):
        node_value = node.obj_repr()
        new = node.proto(node_value[:self.index] + node_value[self.index + self.length:])
        reverse = StringInsertOperation(self.index, node_value[self.index:self.index+self.length])
        return new, reverse

class StringSetOperation(Operation):
    def __init__(self, value):
        self.value = value

    def apply(self, node):
        new = node.proto(self.value)
        reverse = StringSetOperation(node.obj_repr())
        return new, reverse

### Boolean operations.

class BooleanSetOperation(Operation):
    def __init__(self, value):
        self.value = value

    def apply(self, node):
        new = node.proto(self.value)
        reverse = BooleanSetOperation(not self.value)
        return new, reverse

### List operations.

class ListInsertOperation(Operation):
    def __init__(self, index, value):
        self.index = index
        self.value = value
    def apply(self, node):
        new = node.proto(children=node.children[:self.index] + self.value + node.children[self.index:])
        reverse = ListDeleteOperation(self.index, len(self.value))
        return new, reverse
        
class ListDeleteOperation(Operation):
    def __init__(self, index, length):
        self.index = index
        self.length = length

    def apply(self, node):
        new = node.proto(children=node.children[:self.index] + node.children[self.index + self.length:])
        reverse = ListInsertOperation(self.index, node.children[self.index:self.index+self.length])
        return new, reverse

class ListSetIndexOperation(Operation):
    def __init__(self, index, value):
        self.index = index
        self.value = value

    def apply(self, node):
        old = node.children[self.index]
        node.children[self.index] = self.value
        reverse = ListSetIndexOperation(self.index, old)
        return node, reverse

class ListApplyIndexOperation(Operation):
    def __init__(self, index, operation):
        self.index = index
        self.operation = operation

    def apply(self, node):
        new, reverse = self.operation.apply(node.children[self.index])
        reverse_op = ListApplyIndexOperation(self.index, reverse)
        node.children[self.index] = new
        return node, reverse_op

### Dictionary Operations.
### This is tricky.
class DictKeyApplyOperation(Operation):
    def __init__(self, key, operation):
        self.key = key
        self.operation = operation

    def apply(self, node):
        child = node.get_path(self.key)
        new, reverse = self.operation.apply(child)
        node.set_path(self.key, new)
        reverse_op = DictKeyApplyOperation(self.key, reverse)
        return node, reverse_op
        