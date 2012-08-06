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
from check_mysql import MySqlChecker

class TestMySqlChecker(TestPlugin):
    def setUp(self):
        self.checker = MySqlChecker()
        try:
            os.mkdir("./status/")
        except OSError:
            pass
        print 'check_mysql'

    def test_get_queries_per_second(self):
        self.assert_status("-t QUERIES_PER_SECOND -z mysql_test -d ./status/")

    def test_get_slow_queries(self):
        self.assert_status("-t SLOW_QUERIES -z mysql_test -d ./status/")

    def test_get_row_opertions(self):
        self.assert_status("-t ROW_OPERATIONS -z mysql_test -d ./status/")

    def test_get_transactions(self):
        self.assert_status("-t TRANSACTIONS -z mysql_test -d ./status/")

    #def test_get_network_traffic(self, request):
    #    pass

    def test_get_connections(self):
        self.assert_status("-t CONNECTIONS -z mysql_test -d ./status/")

    def test_get_bytes_transfer(self):
        self.assert_status("-t TOTAL_BYTES -z mysql_test -d ./status/")

    def test_get_select_stats(self):
        self.assert_status("-t SELECTS -z mysql_test -d ./status/")

    #def test_get_replication(self, request):
    #    pass

if __name__ == "__main__":
    unittest.main()