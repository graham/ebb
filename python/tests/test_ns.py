import unittest
import json
import sys
import json

import trees
import ns
import ops
import helper

class TestNamespace(unittest.TestCase):
    def test_execute_works(self):
        n = ns.Namespace('testing')
        op = ops.NumberIncrementOperation(30)
        n.execute('key', [], op)
        
        self.assertEqual(n.get('key').root.obj_repr(), 30)
        self.assertEqual(n.get_value('key'), 30)
        
    def test_no_double_commit(self):
        n = ns.Namespace('testing')
        op = ops.NumberIncrementOperation(30)
        n.execute('key', [], op)
        e = None

        try:
            n.execute('key', [], op)
        except:
            e = "DID"

        self.assertEqual(e, "DID")

    def test_exec_multiple(self):
        n = ns.Namespace('testing')
        for i in range(0, 10):
            n.execute('key', [], ops.NumberIncrementOperation(10))
        self.assertEqual(n.get_value('key'), 100)

        for i in range(0, 10):
            n.execute('key', [], ops.NumberIncrementOperation(-5))
        self.assertEqual(n.get_value('key'), 50)

    def test_exclude_operation(self):
        n = ns.Namespace('testing')
        
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
        n = ns.Namespace('testing')
        
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

class TestDocument(unittest.TestCase):
    def test_string_insert(self):
        op1 = ops.StringInsertOperation(0, "hello world")
        op2 = ops.StringDeleteOperation(6, 5)
        op3 = ops.StringInsertOperation(6, "sir")

        op22 = ops.StringInsertOperation(0, "well, ")

        d = ns.Document(trees.Node(type='string'))
        d = d.include_operation([], op1, 10)
        d = d.include_operation([], op2, 20)
        d = d.include_operation([], op3, 30)
        self.assertEqual(d.root.obj_repr(), "hello sir")

        d = d.include_operation([], op22, 25)
        self.assertEqual(d.root.obj_repr(), "well, hello sir")

        op4 = ops.StringInsertOperation(6, "that is interesting, ")
        d = d.include_operation([], op4)
        self.assertEqual(d.root.obj_repr(), "well, that is interesting, hello sir")
        
        d = d.exclude_operation(op4)
        self.assertEqual(d.root.obj_repr(), "well, hello sir")

    def test_string_mega(self):
        words = "Hello world, I want to be your friend, but frankly, you're not cool enough.".split(' ')
        lops = []
        index = 0
        
        for i in words:
            lops.append(ops.StringInsertOperation(index, i + ' '))
            index += len(i) + 1

        for l in lops:
            d = ns.Document(trees.Node.from_obj(''))
            for index, i in enumerate(lops):
                d = d.include_operation([], i, ts=index)

            op = l
            d = d.exclude_operation(op)
            self.assertEqual(d.root.obj_repr(), ''.join([i.text for i in lops if i != op]))

            d = d.include_operation([], op, ts=index)
            self.assertEqual(d.root.obj_repr(), ''.join([i.text for i in lops]))

        d = ns.Document(trees.Node.from_obj(''))
        for i in lops:
            d = d.include_operation([], i)
        
        d = d.exclude_operation(lops[9])
        self.assertEqual(d.root.obj_repr(), u"Hello world, I want to be your friend, but you're not cool enough. ")

        new_op = ops.StringInsertOperation(0, "Blarg! ")
        d = d.include_operation([], new_op, ts=20)
        self.assertEqual(d.root.obj_repr(), u"Blarg! Hello world, I want to be your friend, but you're not cool enough. ")

        other_op = ops.StringInsertOperation(67, "asdf, ")
        d = d.include_operation([], other_op, ts=10)
        self.assertEqual(d.root.obj_repr(), u"Blarg! Hello world, I want to be your friend, but you're not cool enough. asdf, ")

        d = d.exclude_operation(lops[1])
        d = d.exclude_operation(lops[5])
        self.assertEqual(d.root.obj_repr(), u"Blarg! Hello I want to your friend, but you're not cool enough. asdf, ")

    def test_list_insert_and_delete(self):
        d = ns.Document(trees.Node.from_obj([1,2,3,4,5]))

        op1 = ops.ListInsertOperation(0, [trees.Node.from_obj(0)])
        d = d.include_operation([], op1)
        self.assertEqual(d.root.obj_repr(), [0,1,2,3,4,5])

        op2 = ops.ListDeleteOperation(2,2)
        d = d.include_operation([], op2)
        self.assertEqual(d.root.obj_repr(), [0,1,4,5])

        d = d.exclude_operation(op1)
        self.assertEqual(d.root.obj_repr(), [1,4,5])

    def test_nested_int_incr(self):
        d = ns.Document(trees.Node.from_obj([1,2,3]))
        
        op1 = ops.NumberIncrementOperation(100)
        d = d.include_operation([0], op1)
        self.assertEqual(d.root.obj_repr(), [101,2,3])
        
        d = d.exclude_operation(op1)
        self.assertEqual(d.root.obj_repr(), [1,2,3])

    def test_super_nested(self):
        d = ns.Document(trees.Node.from_obj([1,{'one':'hello'}, [1,2,3]]))
        
        op1 = ops.NumberIncrementOperation(123)
        d = d.include_operation([2,0], op1)
        self.assertEqual(d.root.obj_repr(), [1,{'one':'hello'}, [124,2,3]])

        op2 = ops.StringInsertOperation(6, " world")
        op3 = ops.DictKeyApplyOperation(['one'], op2)
        
        d = d.include_operation([1], op3)
        self.assertEqual(d.root.obj_repr(), [1,{'one':'hello world'}, [124,2,3]])

    def test_nested_dict_access(self):
        d = ns.Document(trees.Node.from_obj({'key':[1,2,3]}))
        op = ops.NumberIncrementOperation(10)
        d = d.include_operation(['key', 0], op)
        self.assertEqual(d.root.obj_repr(), {'key':[11,2,3]})

        d = d.exclude_operation(op)
        self.assertEqual(d.root.obj_repr(), {'key':[1,2,3]})

    def test_nested_dict_access_multi(self):
        d = ns.Document(trees.Node.from_obj({'key':[1,2,3]}))
        op = ops.NumberIncrementOperation(10)
        d = d.include_operation(['key', 0], op)
        self.assertEqual(d.root.obj_repr(), {'key':[11,2,3]})

        op2 = ops.NumberIncrementOperation(40)
        op3 = ops.NumberIncrementOperation(123)
        
        d = d.include_operation(['key', 1], op2)
        d = d.include_operation(['key', 2], op3)
        self.assertEqual(d.root.obj_repr(), {'key':[11,42,126]})

        d = d.exclude_operation(op)
        self.assertEqual(d.root.obj_repr(), {'key':[1,42,126]})

        d = d.exclude_operation(op3)
        self.assertEqual(d.root.obj_repr(), {'key':[1,42,3]})

    def test_zzz_nested_dict_access_with_rewrite(self):
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

    def test_mega_nest_dict(self):
        data = {
            'father': {
                'first':'tony',
                'last':'abbott',
                'age':63
                },
            'mother': {
                'first':'mary',
                'last':'seaton',
                'age':62
                },
            'info': {
                'first':'graham',
                'last':'abbott',
                'age':28,
                'tags':['awesome', 'asshole', 'dropboxer']
                }
            }
        d = ns.Document(trees.Node.from_obj(data))
        self.assertEqual(d.root.obj_repr(), data)

        op = ops.StringInsertOperation(0, 'sir ')
        op2 = ops.StringInsertOperation(4, ' aka fellini')

        d = d.include_operation(['father','first'], op, ts=10)
        self.assertEqual(d.root.obj_repr()['father']['first'], 'sir tony')

        d = d.include_operation(['father','first'], op2, ts=5)
        self.assertEqual(d.root.obj_repr()['father']['first'], 'sir tony aka fellini')

        d = d.include_operation(['mother', 'age'], ops.NumberIncrementOperation(-20), ts=0)
        self.assertEqual(d.root.obj_repr()['mother']['age'], 42)

        d = d.exclude_operation(op)
        self.assertEqual(d.root.obj_repr()['father']['first'], 'tony aka fellini')

    def test_mega_nest_list(self):
        d = ns.Document(trees.Node.from_obj([ [1,2,3], [4,5,6], [7,8,[9]] ]))

        op = ops.ListInsertOperation(0, [trees.Node.from_obj(333)])
        d = d.include_operation([0], op, ts=1000)
        self.assertEqual(d.root.obj_repr(), [ [333, 1,2,3], [4,5,6], [7,8,[9]] ])

        op2 = ops.ListApplyIndexOperation(2, ops.NumberIncrementOperation(1000))
        d = d.include_operation([0], op2, ts=900)
        self.assertEqual(d.root.obj_repr(), [ [333, 1,2,1003], [4,5,6], [7,8,[9]] ])
        

if __name__ == '__main__':
    unittest.main()

