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
from check_mysql import MySqlChecker

class TestMySqlChecker(TestPlugin):
    def setUp(self):
        self.checker = MySqlChecker()
        print 'check_mysql'

    def test_get_queries_per_second(self):
        self.assert_status("-t QUERIES_PER_SECOND")

    def test_get_slow_queries(self):
        self.assert_status("-t SLOW_QUERIES")

    def test_get_row_opertions(self):
        self.assert_status("-t ROW_OPERATIONS")

    def test_get_transactions(self):
        self.assert_status("-t TRANSACTIONS")

    #def test_get_network_traffic(self, request):
    #    pass

    def test_get_connections(self):
        self.assert_status("-t CONNECTIONS")

    def test_get_bytes_transfer(self):
        self.assert_status("-t TOTAL_BYTES")

    def test_get_select_stats(self):
        self.assert_status("-t SELECTS")

    #def test_get_replication(self, request):
    #    pass

if __name__ == "__main__":
    unittest.main()