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
#     # the current test i'm really worried about.
#     def test_fs_incremental_load(self):
#         x = ns.NamespaceFS('test_namespace')
#         y = ns.NamespaceFS('test_namespace')
#         x.fresh()

#         keys = ['key_%i' % i for i in range(0, 5)]
#         for i in keys:
#             for j in range(0, 2):
#                 op = ops.NumberIncrementOperation(random.randint(100, 1000))
#                 x.execute(i, [], op)
#         x.flush()
#         y.full_load()

#         for i in keys:
#             left = x.get_value(i)
#             right = y.get_value(i)
#             self.assertEqual( left, right )

#         # --- lets make more changes.

#         for i in keys:
#             for j in range(0, 2):
#                 op = ops.NumberIncrementOperation(random.randint(100, 1000))
#                 x.execute(i, [], op)
#         x.flush()

        

#         # now do an incremental load.
#         y.full_load()
        
#         for i in keys:
#             left = x.get_value(i)
#             right = y.get_value(i)
#             self.assertEqual( left, right )

    def test_depth_test(self):
        init = trees.Node.from_obj([1,2,{'one':'hello'}])
        op1 = ops.ListApplyIndexOperation(0, ops.NumberIncrementOperation(50))
        first, revert_first = op1.apply(init)
        self.assertEqual(first.obj_repr(), [51,2,{'one':'hello'}])
        
        op2 = ops.ListApplyIndexOperation(2, ops.DictKeyApplyOperation(['one'], ops.StringInsertOperation(0, 'sup, ')))
        second, revert_second = op2.apply(init)
        self.assertEqual(second.obj_repr(), [1,2,{'one':'sup, hello'}])

        step_back, revert_step_back = revert_second.apply(second)
        self.assertEqual(step_back.obj_repr(), [1,2,{'one':'hello'}])


if __name__ == '__main__':
    unittest.main()

