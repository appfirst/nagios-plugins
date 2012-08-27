'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys
import os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_rootpath, ".."))

import unittest
from test_plugin import TestPlugin
from check_memcached import MemcachedChecker

class TestMemcachedChecker(TestPlugin):
    def setUp(self):
        self.checker = MemcachedChecker()
        try:
            os.mkdir("./status/")
        except OSError:
            pass
        print 'check_memcached'

    def test_get_cmd_set(self):
        self.assert_status("-t OPERATIONS_SET_REQUESTS -z memcached_test -d ./status/")

    def test_get_cmd_get(self):
        self.assert_status("-t OPERATIONS_GET_REQUESTS -z memcached_test -d ./status/")

    def test_get_bytes_read(self):
        self.assert_status("-t BYTES_READ -z memcached_test -d ./status/")

    def test_get_bytes_written(self):
        self.assert_status("-t BYTES_WRITTEN -z memcached_test -d ./status/")

    def test_get_bytes_allocated(self):
        self.assert_status("-t BYTES_ALLOCATED -z memcached_test -d ./status/")

    def test_get_total_items(self):
        self.assert_status("-t TOTAL_ITEMS -z memcached_test -d ./status/")

    def test_get_current_connections(self):
        self.assert_status("-t CURRENT_CONNECTIONS -z memcached_test -d ./status/")

if __name__ == "__main__":
    unittest.main()