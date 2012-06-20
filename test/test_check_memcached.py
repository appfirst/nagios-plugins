'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys, os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, ".."))

from test_plugin import TestPlugin
from check_memcached import MemcachedChecker

class TestMemcachedChecker(TestPlugin):
    def test_check_memcached(self):
        self.checker = MemcachedChecker()
        print ' - testing: check_memcached'
        self.assert_status("-t OPERATIONS_SET_REQUESTS")
        self.assert_status("-t OPERATIONS_GET_REQUESTS")
        self.assert_status("-t BYTES_READ")
        self.assert_status("-t BYTES_WRITTEN")
        self.assert_status("-t BYTES_ALLOCATED")
        self.assert_status("-t TOTAL_ITEMS")
        self.assert_status("-t TOTAL_CONNECTIONS")