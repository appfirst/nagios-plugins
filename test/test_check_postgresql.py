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
        print 'check_postgresql'

    def test_get_connections_active(self):
        self.assert_status("-u postgres -t CONNECTIONS_ACTIVE")

    def test_get_connections_waiting(self):
        self.assert_status("-u postgres -t CONNECTIONS_WAITING")

    def test_get_conenctions_idle(self):
        self.assert_status("-u postgres -t CONNECTIONS_IDLE")

    def test_get_database_size(self):
        self.assert_status("-u postgres -t DATABASE_SIZE")

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