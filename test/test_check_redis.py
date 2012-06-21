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
from check_redis import RedisChecker

class TestRedisChecker(TestPlugin):
    def setUp(self):
        self.checker = RedisChecker()
        print ' - testing: check_redis'

    def test_get_operations_rate(self):
        self.assert_status("-t OPERATIONS_RATE")

    def test_get_memory_used(self):
        self.assert_status("-t MEMORY_USED")

    def test_get_change_since_last_save(self):
        self.assert_status("-t CHANGES_SINCE_LAST_SAVE")

    def test_get_total_keys(self):
        self.assert_status("-t TOTAL_KEYS")

if __name__ == "__main__":
    unittest.main()