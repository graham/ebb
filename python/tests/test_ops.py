import unittest
import json
import sys
import json

import trees
import ops

class TestOperations(unittest.TestCase):
    def test_number(self):
        number = trees.Node.from_obj(123)
        op = ops.NumberIncrementOperation(-23)
        result, reverse = op.apply(number)
        
        self.assertEqual(result.obj_repr(), 100)
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), number.obj_repr())
    
    def test_string_insert(self):
        init = trees.Node.from_obj("hello world")
        op = ops.StringInsertOperation(0, "well, ")
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), "well, hello world")
    
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), init.obj_repr())
    
        op2 = ops.StringInsertOperation(len(result.obj_repr()), ", now more");
        result2, reverse2 = op2.apply(result)
        self.assertEqual(result2.obj_repr(), "well, hello world, now more")
    
    def test_string_delete(self):
        init = trees.Node.from_obj("hello world")
        op = ops.StringDeleteOperation(0, 2)
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), "llo world")
    
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), init.obj_repr())

        op2 = ops.StringDeleteOperation(6,5)
        result, reverse = op2.apply(init)
        self.assertEqual(result.obj_repr(), "hello ")
        
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), init.obj_repr())
    
    def test_string_set(self):
        init = trees.Node.from_obj("hello world")
        op = ops.StringSetOperation("fuck you")
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), "fuck you")
        
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), "hello world")
    
    def test_boolean_set(self):
        init = trees.Node.from_obj(True)
        op = ops.BooleanSetOperation(False)
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), False)
        
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), True)
    
    def test_list_insert(self):
        init = trees.Node.from_obj([1,2,3])
        op = ops.ListInsertOperation(0, [trees.Node.from_obj(-10)])
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), [-10,1,2,3])
        
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), init.obj_repr())
        
    def test_list_delete(self):
        init = trees.Node.from_obj([1,2,3])
        op = ops.ListDeleteOperation(0, 1)
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), [2,3])
        
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), [1,2,3])
    
    def test_list_set_index(self):
        init = trees.Node.from_obj([1,2,3])
        op = ops.ListSetIndexOperation(0, trees.Node.from_obj(100))
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), [100, 2,3])
    
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), [1,2,3])
    
    def test_list_apply_op(self):
        init = trees.Node.from_obj([1,2,3])
        op = ops.ListApplyIndexOperation(0, ops.NumberIncrementOperation(100))
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), [101,2,3])
    
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), [1,2,3])
    
    def test_dict_key_apply(self):
        init = trees.Node.from_obj({'one':'hello'})
        op = ops.DictKeyApplyOperation(['one'], ops.StringInsertOperation(5, ' world'))
        result, reverse = op.apply(init)
        self.assertEqual(result.obj_repr(), {'one':"hello world"})
    
        back, inverse = reverse.apply(result)
        self.assertEqual(back.obj_repr(), {'one':'hello'})

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

    def test_pure_set(self):
        init = trees.Node.from_obj([1,2,3])
        op1 = ops.SetOperation([4,5,6])

        first, reverse_first = op1.apply(init)

        self.assertEqual(first.obj_repr(), [4,5,6])

    def test_move_path_simple(self):
        init = trees.Node.from_obj({'test':123})
        op1 = ops.MovePathOperation(['test'], ['new_path'])
        
        first, revert_first = op1.apply(init)
        self.assertEqual(first.obj_repr(), {'new_path':123})

    def test_move_path_complex(self):
        d = {'key':[1,2,[4,5,{'ok':'value'}]]}
        init = trees.Node.from_obj(d)
        op1 = ops.MovePathOperation(['key', 2, 2, 'ok'], ['key', 2, 2, 'asdf'])
        op2 = ops.MovePathOperation(['key'], ['asdf'])

        first, revert_first = op1.apply(init)
        self.assertEqual(first.obj_repr(), {'key':[1,2,[4,5,{'asdf':'value'}]]})

        second, revert_second = op2.apply(first)
        self.assertEqual(second.obj_repr(), {'asdf':[1,2,[4,5,{'asdf':'value'}]]})

if __name__ == '__main__':
    unittest.main()
