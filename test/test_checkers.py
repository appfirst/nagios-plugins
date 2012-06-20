'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys, os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, ".."))

import unittest
from StringIO import StringIO
import nagios

from check_postgresql import PostgresChecker
from check_memcached import MemcachedChecker
from check_passenger import PassengerChecker
from check_mysql import MySqlChecker
from check_redis import RedisChecker

class TestCheckerBase(unittest.TestCase):
    def assert_status(self, argument):
        # change the standard output to StringIO()
        original_stdout, sys.stdout = sys.stdout, StringIO()
        args = argument.split()
        # get output and exit_code
        exit_code = 0
        try:
            self.checker.run(args)
        except SystemExit as se:
            exit_code = se.code
        output = sys.stdout.getvalue()
        # change the standard output back
        sys.stdout.close()
        sys.stdout = original_stdout
        # print and assert
        print "\targv:   %s" % argument
        print "\tstdout: %s" % output
        self.assertEqual(nagios.Status.to_status(exit_code), "OK")

class TestPostgresChecker(TestCheckerBase):
    def test_check_postgresql(self):
        self.checker = PostgresChecker()
        print ' - testing: check_postgresql'
        self.assert_status("-t TUPLE_READ")
        self.assert_status("-t TUPLE_INSERTED")
        self.assert_status("-t TUPLE_UPDATED")
        self.assert_status("-t TUPLE_DELETED")

class TestMySqlChecker(TestCheckerBase):
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

class TestMemcachedChecker(TestCheckerBase):
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

class TestRedisChecker(TestCheckerBase):
    def test_check_redis(self):
        self.checker = RedisChecker()
        print ' - testing: check_redis'
        self.assert_status("-t OPERATIONS_RATE")
        self.assert_status("-t MEMORY_USED")
        self.assert_status("-t CHANGES_SINCE_LAST_SAVE")
        self.assert_status("-t TOTAL_KEYS")

class TestPassengerChecker(TestCheckerBase):
    def test_check_passenger(self):
        self.checker = PassengerChecker()
        print ' - testing: check_passenger'
        self.assert_status("-t MAX_PROCESSES")
        self.assert_status("-t RUNNING_PROCESSES")
        self.assert_status("-t ACTIVE_PROCESSES")

class TestMongoDBChecker(TestCheckerBase):
    def test_check_mongodb(self):
        pass

class TestResqueChecker(unittest.TestCase):
    def test_check_resque(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()