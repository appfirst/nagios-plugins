'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys
from os import path
_rootpath = path.dirname(path.realpath(__file__))
sys.path.append(path.join(_rootpath, ".."))

import unittest
from test_plugin import TestPlugin
from check_memcached import MemcachedChecker

class TestMemcachedChecker(TestPlugin):
    def setUp(self):
        self.checker = MemcachedChecker()
        print ' - testing: check_memcached'

    def test_get_cmd_set(self):
        self.assert_status("-t OPERATIONS_SET_REQUESTS")

    def test_get_cmd_get(self):
        self.assert_status("-t OPERATIONS_GET_REQUESTS")

    def test_get_bytes_read(self):
        self.assert_status("-t BYTES_READ")

    def test_get_bytes_written(self):
        self.assert_status("-t BYTES_WRITTEN")

    def test_get_bytes_allocated(self):
        self.assert_status("-t BYTES_ALLOCATED")

    def test_get_total_items(self):
        self.assert_status("-t TOTAL_ITEMS")

    def test_get_total_connections(self):
        self.assert_status("-t TOTAL_CONNECTIONS")

if __name__ == "__main__":
    unittest.main()