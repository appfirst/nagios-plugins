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
from check_postgresql import PostgresChecker

class TestPostgresChecker(TestPlugin):
    def setUp(self):
        self.checker = PostgresChecker()
        print ' - testing: check_postgresql'

    def test_get_tuple_read(self):
        self.assert_status("-u postgres -t TUPLE_READ")

    def test_get_tuple_inserted(self):
        self.assert_status("-u postgres -t TUPLE_INSERTED")

    def test_get_tuple_updated(self):
        self.assert_status("-u postgres -t TUPLE_UPDATED")

    def test_get_tuple_deleted(self):
        self.assert_status("-u postgres -t TUPLE_DELETED")

if __name__ == "__main__":
    unittest.main()