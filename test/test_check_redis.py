'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys, os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, ".."))

from test_plugin import TestPlugin
from check_redis import RedisChecker

class TestRedisChecker(TestPlugin):
    def test_check_redis(self):
        self.checker = RedisChecker()
        print ' - testing: check_redis'
        self.assert_status("-t OPERATIONS_RATE")
        self.assert_status("-t MEMORY_USED")
        self.assert_status("-t CHANGES_SINCE_LAST_SAVE")
        self.assert_status("-t TOTAL_KEYS")