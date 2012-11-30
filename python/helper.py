import ops
import trees
from ns import Namespace

# Not really intended to be part of the final product
# but this helper object can help define how developers
# end up interacting with the namespaces. For some creating
# the actual operations might be too difficult.

class NamespaceHelper(Namespace):
    def _parse(self, key):
        res = key.split('/', 1)
        if len(res) > 1:
            k, r = res
            rest = r.split("/")
            return k, rest
        else:
            return res[0], []

    def set_path(self, key, obj):
        x = ops.SetOperation(obj)
        key, path = self._parse(key)
        self.execute(key, path, x)

    def get_path(self, key):
        key, path = self._parse(key)
        doc = self.get(key)
        return doc.root.get_path(path)

    def get_path_value(self, key):
        node = self.get_path(key)
        return node.obj_repr()

    def exists(self, key):
        return key in self.docs

    getp = get_path
    getpv = get_path_value
    setp = set_path

    ## BEGIN INTEGER STUFF
    #increment decrement for integers
    def incr(self, key, amount=1):
        key, path = self._parse(key)
        return self.execute(key,
                            path,
                            ops.NumberIncrementOperation(amount))

    # this is just the opposite as incr
    def decr(self, key, amount=1):
        return self.incr(key, amount * -1)
    ## END INTEGER STUFF

    ## BEGIN LIST OPS
    def rpush(self, key, obj):
        key, path = self._parse(key)
        current = self.get(key)
        op = ops.ListInsertOperation(len(current.root.obj_repr()),
                                     [trees.Node.from_obj(obj)])
        self.execute(key, path, op)

    def lpush(self, key, obj):
        key, path = self._parse(key)
        current = self.get(key)
        op = ops.ListInsertOperation(0,
                                     [trees.Node.from_obj(obj)])
        self.execute(key, path, op)

    def lpop(self, fullkey):
        key, path = self._parse(fullkey)
        current = self.get(key)
        op = ops.ListDeleteOperation(0, 1)
        prev_value = current.get_value(path)

        self.execute(key, path, op)

        if len(prev_value) > 0:
            return prev_value[0]
        else:
            return None

    def rpop(self, fullkey):
        key, path = self._parse(fullkey)
        current = self.get(key)
        op = ops.ListDeleteOperation(len(current.root.obj_repr())-1, 1)
        prev_value = current.get_value(path)

        self.execute(key, path, op)

        if len(prev_value) > 0:
            return prev_value[-1]
        else:
            return None

    def llen(self, fullkey):
        key, path = self._parse(fullkey)
        current = self.get(key)
        op = ops.ListDeleteOperation(len(current.root.obj_repr())-1, 1)
        prev_value = current.get_value(path)
        return len(prev_value)

    def linsert(self, key, index, obj):
        key, path = self._parse(key)
        op = ops.ListInsertOperation(index, [trees.Node.from_obj(obj)])
        self.execute(key, path, op)

    def lset(self, key, index, obj):
        key, path = self._parse(key)
        op = ops.ListSetIndexOperation(index, trees.Node.from_obj(obj))
        self.execute(key, path, op)

    def lrange(self, key, start_index, end_index):
        return self.getpv(key)[start_index:end_index]

    def lindex(self, key, index):
        return self.getpv(key)[index]
    ### END LIST FUNCS

    ### START STRING FUNCTIONS
    ### END STRING FUNCTIONS

x = NamespaceHelper('test')
