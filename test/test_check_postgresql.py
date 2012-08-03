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
        self.assert_status("-t CONNECTIONS_ACTIVE -z postgres_test -d ./status/")

    def test_get_connections_waiting(self):
        self.assert_status("-t CONNECTIONS_WAITING -z postgres_test -d ./status/")

    def test_get_conenctions_idle(self):
        self.assert_status("-t CONNECTIONS_IDLE -z postgres_test -d ./status/")

    def test_get_database_size(self):
        self.assert_status("-t DATABASE_SIZE -z postgres_test -d ./status/")

    def test_get_locks_access(self):
        self.assert_status("-t LOCKS_ACCESS -z postgres_test -d ./status/")

    def test_get_locks_row(self):
        self.assert_status("-t LOCKS_ROW -z postgres_test -d ./status/")

    def test_get_locks_share(self):
        self.assert_status("-t LOCKS_SHARE -z postgres_test -d ./status/")

    def test_get_locks_exclusive(self):
        self.assert_status("-t LOCKS_EXCLUSIVE -z postgres_test -d ./status/")

    def test_get_tuple_read(self):
        self.assert_status("-t TUPLES_READ -z postgres_test -d ./status/")

    def test_get_tuple_inserted(self):
        self.assert_status("-t TUPLES_INSERTED -z postgres_test -d ./status/")

    def test_get_tuple_updated(self):
        self.assert_status("-t TUPLES_UPDATED -z postgres_test -d ./status/")

    def test_get_tuple_deleted(self):
        self.assert_status("-t TUPLES_DELETED -z postgres_test -d ./status/")

if __name__ == "__main__":
    unittest.main()