import unittest
import json
import sys
import json
import random

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

    # def tests_storage_basic(self):
    #     x = ns.NamespaceFS('test_namespace')
    #     op = ops.NumberIncrementOperation(10)

    #     x.execute('test', [], op)
    #     newx = x.get('test')
        
    #     self.assertEqual(newx.root.obj_repr(), 10)
    #     x.flush()


if __name__ == '__main__':
    unittest.main()

