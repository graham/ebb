import unittest
import json
import sys
import json

import trees
import ns
import ops

class TestNamespace(unittest.TestCase):
    def test_execute_works(self):
        n = ns.Namespace('testing')
        op = ops.NumberIncrementOperation(30)
        n.execute('key', op)

        self.assertEqual(n.get('key').root.obj_repr(), 30)
        self.assertEqual(n.get_value('key'), 30)
        
    def test_no_double_commit(self):
        n = ns.Namespace('testing')
        op = ops.NumberIncrementOperation(30)
        n.execute('key', op)
        e = None

        try:
            n.execute('key', op)
        except:
            e = "DID"

        self.assertEqual(e, "DID")

    def test_exec_multiple(self):
        n = ns.Namespace('testing')
        for i in range(0, 10):
            n.execute('key', ops.NumberIncrementOperation(10))
        self.assertEqual(n.get_value('key'), 100)

        for i in range(0, 10):
            n.execute('key', ops.NumberIncrementOperation(-5))
        self.assertEqual(n.get_value('key'), 50)

    def test_exclude_operation(self):
        n = ns.Namespace('testing')
        
        op1 = ops.NumberIncrementOperation(11)
        op2 = ops.NumberIncrementOperation(12)
        op3 = ops.NumberIncrementOperation(13)

        for i in (op1, op2, op3):
            n.execute('key', i)

        self.assertEqual(n.get_value('key'), 36)

        d = n.get('key')
        newd = d.exclude_operation(op2)
        self.assertEqual(newd.root.obj_repr(), 24)

        newd2 = newd.exclude_operation(op1)
        self.assertEqual(newd2.root.obj_repr(), 13)

        # lets make sure our previous state is intact.
        self.assertEqual(d.root.obj_repr(), 36)
    
    def test_include_operation(self):
        n = ns.Namespace('testing')
        
        op1 = ops.NumberIncrementOperation(11)
        op2 = ops.NumberIncrementOperation(12)
        op3 = ops.NumberIncrementOperation(13)

        op4 = ops.NumberIncrementOperation(14)

        for i in (op1, op2, op3):
            n.execute('key', i)

        self.assertEqual(n.get_value('key'), 36)

        d = n.get('key')
        newd = d.include_operation('', op4, ts=0)
        self.assertEqual(newd.root.obj_repr(), 50)
    

class TestDocument(unittest.TestCase):
    def test_string_insert(self):
        op1 = ops.StringInsertOperation(0, "hello world")
        op2 = ops.StringDeleteOperation(6, 5)
        op3 = ops.StringInsertOperation(6, "sir")

        op22 = ops.StringInsertOperation(0, "well, ")

        d = ns.Document(trees.Node(type='string'))
        d = d.include_operation('', op1, 10)
        d = d.include_operation('', op2, 20)
        d = d.include_operation('', op3, 30)
        self.assertEqual(d.root.obj_repr(), "hello sir")

        d = d.include_operation('', op22, 25)
        self.assertEqual(d.root.obj_repr(), "well, hello sir")

        op4 = ops.StringInsertOperation(6, "that is interesting, ")
        d = d.include_operation('', op4)
        self.assertEqual(d.root.obj_repr(), "well, that is interesting, hello sir")
        
        d = d.exclude_operation(op4)
        self.assertEqual(d.root.obj_repr(), "well, hello sir")

    def test_list_insert_and_delete(self):
        d = ns.Document(trees.Node.from_obj([1,2,3,4,5]))

        op1 = ops.ListInsertOperation(0, [trees.Node.from_obj(0)])
        d = d.include_operation('', op1)
        self.assertEqual(d.root.obj_repr(), [0,1,2,3,4,5])

        op2 = ops.ListDeleteOperation(2,2)
        d = d.include_operation('', op2)
        self.assertEqual(d.root.obj_repr(), [0,1,4,5])

        d = d.exclude_operation(op1)
        self.assertEqual(d.root.obj_repr(), [1,4,5])

    def test_nested_int_incr(self):
        d = ns.Document(trees.Node.from_obj([1,2,3]))
        
        op1 = ops.NumberIncrementOperation(100)
        d = d.include_operation('0', op1)
        self.assertEqual(d.root.obj_repr(), [101,2,3])
        
        d = d.exclude_operation(op1)
        self.assertEqual(d.root.obj_repr(), [1,2,3])


if __name__ == '__main__':
    unittest.main()
