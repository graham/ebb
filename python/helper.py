import ops
from ns import Namespace

class NamespaceHelper(Namespace):
    def _parse(self, key):
        res = key.split('.', 1)
        if len(res) > 1:
            k, r = res.split(".", 1)
            rest = r.split(".")
            return k, rest
        else:
            return res[0], []

    def incr(self, key, amount=1):
        key, path = self._parse(key)
        return self.execute(key,
                            path,
                            ops.NumberIncrementOperation(amount))

    # this is just the opposite as incr
    def decr(self, key, amount=1):
        return self.incr(key, amount * -1)
    
    def s_insert(self, key, index, s):
        pass
    def s_delete(self, key, index, length):
        pass

x = NamespaceHelper('test')
