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

    def getset(self, key, value):
        current = self.get_path(key)
        self.set_path(key, value)
        return current

    def getsetv(self, key, value):
        return self.getset(key, value).obj_repr()

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

    def get_path_value_meta(self, key):
        key, path = self._parse(key)
        doc = self.get(key)
        return doc.root.get_path(path).obj_repr(), key, path

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
    def rpush(self, fullkey, obj):
        current, key, path = self.get_path_value_meta(fullkey)
        op = ops.ListInsertOperation(len(current),
                                     [trees.Node.from_obj(obj)])
        self.execute(key, path, op)

    def lpush(self, fullkey, obj):
        key, path = self._parse(fullkey)
        op = ops.ListInsertOperation(0,
                                     [trees.Node.from_obj(obj)])
        self.execute(key, path, op)

    def lpop(self, fullkey):
        current, key, path = self.get_path_value_meta(fullkey)
        op = ops.ListDeleteOperation(0, 1)
        self.execute(key, path, op)

        if len(current) > 0:
            return current[0]
        else:
            return None

    def rpop(self, fullkey):
        current, key, path = self.get_path_value_meta(fullkey)
        op = ops.ListDeleteOperation(len(current) - 1, 1)

        self.execute(key, path, op)

        if len(current) > 0:
            return current[-1]
        else:
            return None

    def llen(self, fullkey):
        current, key, path = self.get_path_value_meta(fullkey)
        return len(current)

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
    def sinsert(self, fullkey, index, s):
        op = ops.StringInsertOperation(index, s)
        key, path = self._parse(fullkey)
        self.execute(key, path, op)

    def sdelete(self, fullkey, index, length):
        op = ops.StringDeleteOperation(index, length)
        key, path = self._parse(fullkey)
        self.execute(key, path, op)

    def sappend(self, key, s):
        current = self.get_path_value(key)
        return self.sinsert(key, len(current), s)

    def sprepend(self, key, s):
        self.sinsert(key, 0, s)

    def slen(self, key):
        return len(self.get_path_value(key))
    ### END STRING FUNCTIONS


x = NamespaceHelper('test')
