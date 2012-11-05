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
    # the current test i'm really worried about.
    def test_zzz_nested_dict_access_with_rewrite(self):
        # after writing a test like this i understand why quickcheck exists.
        
        d = ns.Document(trees.Node.from_obj({'key':[1,2,3], 'word':1}))

        op_d = ops.ListInsertOperation(0, [trees.Node.from_obj(-1), trees.Node.from_obj(-2)])
        op_after = ops.ListInsertOperation(3, [trees.Node.from_obj("hello world")])
        op2 = ops.NumberIncrementOperation(40)
        op3 = ops.NumberIncrementOperation(123)
        op4 = ops.NumberIncrementOperation(100)
        
        d = d.include_operation(['key', 0], op2, ts=10)
        d = d.include_operation(['key', 1], op3, ts=20)
        d = d.include_operation(['word'], op4, ts=30)
        self.assertEqual(d.root.obj_repr(), {'key':[1+40,2+123,3], 'word':1+100})

        d = d.include_operation(['key'], op_d, ts=5)
        self.assertEqual(d.root.obj_repr(), {'key':[-1, -2, 41, 125, 3], 'word':101})

        d = d.include_operation(['key'], op_after, ts=1)
        self.assertEqual(d.root.obj_repr(), {'key':[-1,-2,1,42,126, "hello world"], 'word':101})

    def test_fs_storage_reload_from_disk(self):
        pass
                         
if __name__ == '__main__':
    unittest.main()

