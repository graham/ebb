import unittest
import json
import sys
import json

import trees

class TestTrees(unittest.TestCase):
    def test_number(self):
        x = trees.Node()
        x.type = trees.TYPES['number']
        x.value = json.dumps(100)
        self.assertEqual(x.obj_repr(), 100)

    def test_string(self):
        x = trees.Node(type='string')
        x.value = json.dumps('hello world')
        self.assertEqual(x.obj_repr(), u'hello world')

    def test_boolean(self):
        x = trees.Node(type='boolean')
        x.value = json.dumps(True)
        self.assertEqual(x.obj_repr(), True)

        x.value = json.dumps(False)
        self.assertEqual(x.obj_repr(), False)

    def test_list(self):
        x = trees.Node(type='list')
        l = ['one','two','three','four']
        for i in l:
            y = trees.Node(type='string')
            y.value = json.dumps(i)
            x.children.append(y)
        self.assertEqual(x.obj_repr(), l)

    def test_hash(self):
        x = trees.Node(type='hash')
        l = dict(one=1, two=2, three=3, four=4)
        for i in l:
            v = l[i]
            y = trees.Node(type='number')
            y.attr['key'] = i
            y.value = json.dumps(v)
            x.children.append(y)
        self.assertEqual(x.obj_repr(), l)

    def test_nested(self):
        x = trees.Node(type='hash')
        l = dict(three=[ {'one':1}, {'two':True} ])

        first = trees.Node(type='hash')
        first_obj = trees.Node(type='number')
        first_obj.attr['key'] = 'one'
        first_obj.set_value(1)
        first.children.append(first_obj)

        second = trees.Node(type='hash')
        second_obj = trees.Node(type='boolean')
        second_obj.attr['key'] = 'two'
        second_obj.set_value(True)
        second.children.append(second_obj)

        three = trees.Node(type='list')
        three.children.append(first)
        three.children.append(second)
        three.attr['key'] = 'three'

        x.children.append(three)

        self.assertEqual(l, x.obj_repr())

    def test_getter(self):
        x = trees.Node(type='hash')
        l = dict(three=[ {'one':1}, {'two':True} ])

        first = trees.Node(type='hash')
        first_obj = trees.Node(type='number')
        first_obj.attr['key'] = 'one'
        first_obj.set_value(1)
        first.children.append(first_obj)

        second = trees.Node(type='hash')
        second_obj = trees.Node(type='boolean')
        second_obj.attr['key'] = 'two'
        second_obj.set_value(True)
        second.children.append(second_obj)

        three = trees.Node(type='list')
        three.children.append(first)
        three.children.append(second)
        three.attr['key'] = 'three'

        x.children.append(three)

        leaf = x.get_path('three.0.one')
        self.assertEqual(leaf.obj_repr(), 1)
        
    def test_setter(self):
        x = trees.Node(type='hash')
        l = dict(three=[ {'one':1}, {'two':True} ])

        first = trees.Node(type='hash')
        first_obj = trees.Node(type='number')
        first_obj.attr['key'] = 'one'
        first_obj.set_value(1)
        first.children.append(first_obj)

        second = trees.Node(type='hash')
        second_obj = trees.Node(type='boolean')
        second_obj.attr['key'] = 'two'
        second_obj.set_value(True)
        second.children.append(second_obj)

        three = trees.Node(type='list')
        three.children.append(first)
        three.children.append(second)
        three.attr['key'] = 'three'

        x.children.append(three)

        num = 8123819321
        new_leaf = x.set_path('three.0.one', num)
        
        leaf = x.get_path('three.0.one')
        self.assertEqual(leaf.obj_repr(), num)

        x.set_path('three.1.two', 'blarg')
        leaf = x.get_path('three.1.two')
        self.assertEqual(leaf.obj_repr(), 'blarg')

        x.set_path('three.1', [1,2,3])
        leaf = x.get_path('three')
        self.assertEqual(leaf.obj_repr(), [{'one':num}, [1,2,3]])

    def test_from_obj(self):
        l = [1,2,3]
        n = trees.Node.from_obj(l)
        self.assertEqual(n.obj_repr(), l)

    def test_remove(self):
        l = [1,2,3, {'key':'value'}]
        n = trees.Node.from_obj(l)
        self.assertEqual(n.obj_repr(), l)

        n.remove_path('0')
        self.assertEqual(n.obj_repr(), [2,3, {'key':'value'}])

        n.remove_path('2.key')
        self.assertEqual(n.get_path('2').obj_repr(), {})
        

if __name__ == '__main__':
    unittest.main()
