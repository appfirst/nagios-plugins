'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys, os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, ".."))

from test_plugin import TestPlugin
from check_mysql import MySqlChecker

class TestMySqlChecker(TestPlugin):
    def test_check_mysql(self):
        self.checker = MySqlChecker()
        print ' - testing: check_mysql'
        self.assert_status("-t QUERIES_PER_SECOND")
        self.assert_status("-t SLOW_QUERIES")
        self.assert_status("-t ROW_OPERATIONS")
        self.assert_status("-t TRANSACTIONS")
        self.assert_status("-t CONNECTIONS")
        self.assert_status("-t TOTAL_BYTES")
        self.assert_status("-t SELECTS")