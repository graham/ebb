import unittest
import json
import sys
import json

import trees
import ns
import ops
import helper

class TestNamespace(unittest.TestCase):
    def create_namespace(self, title):
        return ns.Namespace(title)

    def test_execute_works(self):
        n = self.create_namespace('testing')
        op = ops.NumberIncrementOperation(30)
        n.execute('key', [], op)
        
        self.assertEqual(n.get('key').root.obj_repr(), 30)
        self.assertEqual(n.get_value('key'), 30)
        
    def test_no_double_commit(self):
        n = self.create_namespace('testing')
        op = ops.NumberIncrementOperation(30)
        n.execute('key', [], op)
        e = None

        try:
            n.execute('key', [], op)
        except:
            e = "DID"

        self.assertEqual(e, "DID")

    def test_exec_multiple(self):
        n = self.create_namespace('testing')
        for i in range(0, 10):
            n.execute('key', [], ops.NumberIncrementOperation(10))
        self.assertEqual(n.get_value('key'), 100)

        for i in range(0, 10):
            n.execute('key', [], ops.NumberIncrementOperation(-5))
        self.assertEqual(n.get_value('key'), 50)

    def test_exclude_operation(self):
        n = self.create_namespace('testing')
        
        op1 = ops.NumberIncrementOperation(11)
        op2 = ops.NumberIncrementOperation(12)
        op3 = ops.NumberIncrementOperation(13)

        for i in (op1, op2, op3):
            n.execute('key', [], i)

        self.assertEqual(n.get_value('key'), 36)

        d = n.get('key')
        newd = d.exclude_operation(op2)
        self.assertEqual(newd.root.obj_repr(), 24)

        newd2 = newd.exclude_operation(op1)
        self.assertEqual(newd2.root.obj_repr(), 13)

        #lets make sure our previous state is intact.
        self.assertEqual(d.root.obj_repr(), 36)
    
    def test_include_operation(self):
        n = self.create_namespace('testing')
        
        op1 = ops.NumberIncrementOperation(11)
        op2 = ops.NumberIncrementOperation(12)
        op3 = ops.NumberIncrementOperation(13)

        op4 = ops.NumberIncrementOperation(14)

        for i in (op1, op2, op3):
            n.execute('key', [], i)

        self.assertEqual(n.get_value('key'), 36)

        d = n.get('key')
        newd = d.include_operation([], op4, ts=0)
        self.assertEqual(newd.root.obj_repr(), 50)

if __name__ == '__main__':
    unittest.main()

