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
        x.purge_disk()
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

        path_to_state = '%s/%s/%s_%s' % (x.ROOT, x.DIR_WITH_CURRENT_STATE, hkey, op._id)
        path_to_commit = '%s/%s/%s' % (x.ROOT, x.DIR_WITH_CHANGES, op._id)

        self.assertTrue(os.path.exists(path_to_state))
        self.assertTrue(os.path.exists(path_to_commit))

        value = 10
        path = []

        self.assertEqual(json.loads(open(path_to_state).read()), value)
        self.assertEqual(json.loads(open(path_to_commit).read()),
                         [key, path, [u'NumberIncrementOperation', unicode(op._id), value]])

if __name__ == '__main__':
    unittest.main()

