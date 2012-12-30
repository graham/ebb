import time
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

class TestCurrent(unittest.TestCase):
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
        x.flush()

        #---------

        y = ns.NamespaceFS('test_namespace')
        y.full_load()

        for i in keys:
            left = x.get_value(i)
            right = y.get_value(i)
            self.assertEqual( left, right )

    def test_fs_storage_with_conflict(self):
        x = ns.NamespaceFS('test_namespace')
        y = ns.NamespaceFS('test_namespace')
        y.META_ROOT = '/tmp/local2/'

        x.purge()
        y.purge()

        x.init()
        y.init()

        keys = ['key_%i' % i for i in range(0, 10)]
        for i in keys:
            for j in range(0, 5):
                op = ops.NumberIncrementOperation(random.randint(100, 1000))
                x.execute(i, [], op)
            x.flush()
        x.flush()

        x_op = ops.NumberIncrementOperation(100)
        y_op = ops.NumberIncrementOperation(500)

        y.execute('key_1', [], y_op)
        x.execute('key_1', [], x_op)

        x.flush()
        y.flush()

        x.full_load()
        y.full_load()

        y.flush()
        x.flush()
        self.assertEqual(x.get_value('key_1'), y.get_value('key_1'))
        
if __name__ == '__main__':
    unittest.main()

