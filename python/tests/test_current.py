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
import helper

class TestCurrent(unittest.TestCase):

    def test_fs_storage_with_list(self):
        x = helper.NamespaceHelper(ns.NamespaceFS('test_namespace'))
        y = helper.NamespaceHelper(ns.NamespaceFS('test_namespace'))
        y.ns.META_ROOT = '/tmp/local2/'

        x.ns.purge()
        y.ns.purge()

        x.ns.init()
        y.ns.init()

        x.incr('key', 100)
        y.incr('key', 100)

        x.ns.flush()
        y.ns.flush()

        x.ns.full_load()
        x.ns.flush()
        y.ns.full_load()
        y.ns.flush()
        
        self.assertEqual(x.get_value('key'), y.get_value('key'))

        x.lpush('list', 'asdf')
        y.lpush('list', '9292939129391239')

        x.ns.flush()
        y.ns.flush()

        x.ns.full_load()
        x.ns.flush()
        y.ns.full_load()
        y.ns.flush()

        print x.get_value('list')
        print y.get_value('list')

        print x.get('list').history_buffer
        print y.get('list').history_buffer
        

        
if __name__ == '__main__':
    unittest.main()

