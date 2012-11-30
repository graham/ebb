import unittest
import json
import sys
import json
import random
import hashlib
import os

import trees
import ns
import ops

class TestFSStorage(unittest.TestCase):
    def test_using_correct_contructor(self):
        x = ns.Namespace('test_namespace')
        x.constructor = ns.Document

        x.execute('test', [], ops.NumberIncrementOperation(10))
        self.assertEqual(x.get('test').root.obj_repr(), 10)
        self.assertEqual(x.get('test').__class__, ns.Document)

        x.execute('test', [], ops.NumberIncrementOperation(10))
        self.assertEqual(x.get('test').__class__, ns.Document)

    def tests_storage_basic(self):
        x = ns.NamespaceFS('test_namespace')
        x.purge()
        x.init()
        op = ops.NumberIncrementOperation(10)

        key = 'test'
        hkey = hashlib.md5(key).hexdigest()

        x.execute(key, [], op)
        newx = x.get(key)
        
        self.assertEqual(newx.root.obj_repr(), 10)

        x.flush()
        self.assertEqual(x.dirty_docs, {})
        self.assertEqual(x.dirty_ops, [])

        path_to_state = '%s/%s/%s_%s' % (x.SYNC_ROOT, x.DIR_WITH_CURRENT_STATE, hkey, op._id)
        path_to_commit = '%s/%s/%s' % (x.SYNC_ROOT, x.DIR_WITH_CHANGES, op._id)

        self.assertTrue(os.path.exists(path_to_state))
        self.assertTrue(os.path.exists(path_to_commit))

        value = 10
        path = []

        self.assertEqual(json.loads(open(path_to_state).read()), [key, value])
        self.assertEqual(json.loads(open(path_to_commit).read()),
                         [key, path, [u'NumberIncrementOperation', unicode(op._id), value]])

    def test_fs_storage_reload_from_disk(self):
        x = ns.NamespaceFS('test_namespace')
        x.purge()
        x.init()

        keys = ['key_%i' % i for i in range(0, 10)]
        for i in keys:
            for j in range(0, 5):
                op = ops.NumberIncrementOperation(random.randint(100, 1000))
                x.execute(i, [], op)
        
        x.flush()

        #---------

        y = ns.NamespaceFS('test_namespace')
        y.full_load()

        for i in keys:
            left = x.get_value(i)
            right = y.get_value(i)
            self.assertEqual( left, right )


if __name__ == '__main__':
    unittest.main()

