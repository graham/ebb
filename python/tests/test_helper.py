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
from helper import NamespaceHelper

class TestHelper(unittest.TestCase):
    def test_gets(self):
        n = NamespaceHelper('test')

        dd = {
            'one':[1,2,3],
            'two': {
                'point':1,
                'p':2,
                'll':[3,2,1]
                }
            }

        n.set_path('test', dd)

        self.assertEqual(False, 'test/one' in n.docs)
        self.assertEqual(False, n.exists('test/one'))

        self.assertEqual(n.get_value('test'), dd)
        self.assertEqual(n.get_path('test/one').obj_repr(), [1,2,3])
        self.assertEqual(n.get_path_value('test/one'), [1,2,3])

        self.assertEqual(n.getpv('test/two/point'), 1)
        n.incr('test/two/point', 1)
        self.assertEqual(n.getpv('test/two/point'), 2)

    def test_basic_incr(self):
        x = NamespaceHelper("test_namespace")
        x.incr("test", 1)

        self.assertEqual(x.get("test").root.obj_repr(), 1)

        for i in range(0, 10):
            x.incr("test", 1)
        
        self.assertEqual(x.get("test").root.obj_repr(), 11)

        x.decr("test", 10)
        
        self.assertEqual(x.get("test").root.obj_repr(), 1)

    def test_complex_incr(self):
        x = NamespaceHelper("test")
        x.set_path("test", {})
        x.incr("test/one", 1)
        x.incr("test/one", 1)

        self.assertEqual(x.get_value("test"), {"one":2})

    def test_rpush(self):
        x = NamespaceHelper("test")
        x.set_path("list", [])
        x.rpush("list", 1)
        x.rpush("list", 2)
        x.rpush("list", 3)

        self.assertEqual(x.get_value("list"), [1,2,3])

    def test_lpush(self):
        x = NamespaceHelper("test")
        x.set_path("list", [])
        x.lpush("list", 1)
        x.lpush("list", 2)
        x.lpush("list", 3)

        self.assertEqual(x.get_value("list"), [3,2,1])

    def test_linsert(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3])
        self.assertEqual(x.get_value("list"), [1,2,3])
        
        x.linsert("list", 1, 100)
        self.assertEqual(x.get_value("list"), [1,100,2,3])

    def test_lpop(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3,4])
        
        self.assertEqual(x.lpop("list"), 1)
        self.assertEqual(x.lpop("list"), 2)
        self.assertEqual(x.get_value("list"), [3,4])

    def test_rpop(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3,4])

        self.assertEqual(x.rpop("list"), 4)
        self.assertEqual(x.rpop("list"), 3)
        self.assertEqual(x.get_value("list"), [1,2])

    def test_llen(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3,4])
        self.assertEqual(x.llen('list'), 4)

        x.lpop('list')
        self.assertEqual(x.llen('list'), 3)

    def test_lset(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3,4])

        x.lset("list", 1, 321)
        self.assertEqual(x.get_value('list'), [1,321,3,4])

    def test_lrange(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3,4])
        self.assertEqual(x.lrange('list',1,3), [2,3])

    def test_lindex(self):
        x = NamespaceHelper("test")
        x.set_path("list", [1,2,3,4])
        self.assertEqual(x.lindex('list', 1), 2)

if __name__ == "__main__":
    unittest.main()
