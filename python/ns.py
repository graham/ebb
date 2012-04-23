import trees
import ops
import time
import json

class Namespace(object):
    def __init__(self, name):
        self.name = name
        self.docs = {}

    def execute(self, key, operation):
        if key in self.docs:
            doc = self.docs[key]
        else:
            doc = Document()
        doc.execute(key.split('.', 1)[-1], operation)
        self.docs[key] = doc

    def get(self, key):
        return self.docs[key]

class Document(object):
    def __init__(self, root=None, type=None):
        self.root = root
        self.history_buffer = []
    
    def pack(self):
        s = []
        for i in self.history_buffer:
            s.append(json.dumps([i[0], i[1], i[2].pack()]))
        return '\n'.join(s)

    @classmethod
    def unpack(self, type, data):
        n = Document(type=type)
        for i in data.split('\n'):
            ts, path, operation = json.loads(i)
            n.execute(path, ops.unpack(operation), ts)
        return n
    
    def execute(self, path, operation, ts=None):
        if ts == None:
            ts = time.time()
        if self.root == None:
            self.root = trees.Node(type=operation.for_type)

        new, reverse = operation.apply(self.root)
        self.root = new
        self.history_buffer.append([ts, path, operation, reverse])

    def apply_external_ops(self, ops):
        pass

    def undo_shift_redo(self, ops):
        pass


