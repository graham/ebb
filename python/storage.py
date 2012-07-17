import hashlib
import json
import os

class Storage(object):
    def __init__(self, root_folder):
        self.root = root_folder

    def _path_to_key(self, key):
        s = hashlib.sha1()
        s.update(key)
        return self.root + '/' + s.hexdigest()

    def _path_to_operation(self, key, operation):
        return self._path_to_key(key) + '/' + operation._id

    def store(self, key, operation):
        fpath = self._path_to_operation(key, operation)
        existed = os.path.exists(fpath)

        if not os.path.exists(self._path_to_key(key)):
            os.mkdir(self._path_to_key(key))

        f = open(fpath, 'w')
        f.write(json.dumps(operation.pack()))
        f.close()

        return existed

    def read(self, key, operation):
        fpath = self._path_to_operation(key, operation)
        
        if os.path.exists(fpath):
            return json.loads(open(fpath).read())
        else:
            return None

    def readall(self, k):
        def gen(key, list_of_ops):
            for i in list_of_ops:
                yield self.read(key, i)

        l = os.listdir(self._path_to_operation(k, ''))
        l.sort()
        return gen(k, l)

if __name__ == '__main__':
    from ops import NumberIncrementOperation
    s = Storage('data')
    nio = NumberIncrementOperation(123)
    s.store('test', nio)
    
