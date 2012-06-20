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

from check_postgresql import PostgresChecker
from check_memcached import MemcachedChecker
from check_passenger import PassengerChecker
from check_mysql import MySqlChecker
from check_redis import RedisChecker

class TestCheckerBase(unittest.TestCase):
    def assert_status(self, argument):
        original_stdout, sys.stdout = sys.stdout, StringIO()
        args = argument.split()
        try:
            self.checker.run(args)
        except SystemExit as se:
            exit_code = se.code
        out = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = original_stdout
        success = False
        print out,
        for status_code in range(3):
            if status_code == exit_code:
                success = True
#        if exit_code == 3 and "cannot get service status." not in out:
#            success = True
        self.assertTrue(success, "cannot get service status.")

class TestPostgresChecker(TestCheckerBase):
    def test_check_postgresql(self):
        self.checker = PostgresChecker()
        print ' - testing: check_postgresql'
        self.assert_status("-w 1000 -c 2000 -t TUPLE_READ")
        self.assert_status("-w 1000 -c 2000 -t TUPLE_INSERTED")
        self.assert_status("-w 1000 -c 2000 -t TUPLE_UPDATED")
        self.assert_status("-w 1000 -c 2000 -t TUPLE_DELETED")

class TestMySqlChecker(TestCheckerBase):
    def test_check_mysql(self):
        self.checker = MySqlChecker()
        print ' - testing: check_mysql'
        self.assert_status("-w 1000 -c 2000 -t QUERIES_PER_SECOND")
        self.assert_status("-w 1000 -c 2000 -t SLOW_QUERIES")
        self.assert_status("-w 1000 -c 2000 -t ROW_OPERATIONS")
        self.assert_status("-w 1000 -c 2000 -t TRANSACTIONS")
        self.assert_status("-w 1000 -c 2000 -t CONNECTIONS")
        self.assert_status("-w 1000 -c 2000 -t TOTAL_BYTES")
        self.assert_status("-w 1000 -c 2000 -t SELECTS")

class TestMemcachedChecker(TestCheckerBase):
    def test_check_memcached(self):
        self.checker = MemcachedChecker()
        print ' - testing: check_memcached'
        self.assert_status("-w 1000 -c 2000 -t OPERATIONS_SET_REQUESTS")
        self.assert_status("-w 1000 -c 2000 -t OPERATIONS_GET_REQUESTS")
        self.assert_status("-w 1000 -c 2000 -t BYTES_READ")
        self.assert_status("-w 1000 -c 2000 -t BYTES_WRITTEN")
        self.assert_status("-w 1000 -c 2000 -t BYTES_ALLOCATED")
        self.assert_status("-w 1000 -c 2000 -t TOTAL_ITEMS")
        self.assert_status("-w 1000 -c 2000 -t TOTAL_CONNECTIONS")

class TestRedisChecker(TestCheckerBase):
    def test_check_redis(self):
        self.checker = RedisChecker()
        print ' - testing: check_redis'
        self.assert_status("-w 1000 -c 2000 -t OPERATIONS_RATE")
        self.assert_status("-w 1000 -c 2000 -t MEMORY_USED")
        self.assert_status("-w 1000 -c 2000 -t CHANGES_SINCE_LAST_SAVE")
        self.assert_status("-w 1000 -c 2000 -t TOTAL_KEYS")

class TestPassengerChecker(TestCheckerBase):
    def test_check_passenger(self):
        self.checker = PassengerChecker()
        print ' - testing: check_passenger'
        self.assert_status("-w 1000 -c 2000 -t MAX_PROCESSES")
        self.assert_status("-w 1000 -c 2000 -t RUNNING_PROCESSES")
        self.assert_status("-w 1000 -c 2000 -t ACTIVE_PROCESSES")

class TestMongoDBChecker(TestCheckerBase):
    def test_check_mongodb(self):
        pass

class TestResqueChecker(unittest.TestCase):
    def test_check_resque(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()