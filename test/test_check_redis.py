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
from check_redis import RedisChecker

class TestRedisChecker(TestPlugin):
    def setUp(self):
        self.checker = RedisChecker()
        try:
            os.mkdir("./status/")
        except OSError:
            pass
        print 'check_redis'

    def test_get_average_operations_rate(self):
        self.assert_status("-t AVERAGE_OPERATIONS_RATE -z redis_test -d ./status/")

    def test_get_current_operations_rate(self):
        self.assert_status("-t CURRENT_OPERATIONS -z redis_test -d ./status/")

    def test_get_memory_used(self):
        self.assert_status("-t MEMORY_USED -z redis_test -d ./status/")

    def test_get_current_operations(self):
        self.assert_status("-t CURRENT_CHANGES -z redis_test -d ./status/")

    def test_get_change_since_last_save(self):
        self.assert_status("-t CHANGES_SINCE_LAST_SAVE -z redis_test -d ./status/")

    def test_get_total_keys(self):
        self.assert_status("-t TOTAL_KEYS -z redis_test -d ./status/")

if __name__ == "__main__":
    unittest.main()