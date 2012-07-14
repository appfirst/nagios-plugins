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
from check_mongodb import MongoDBChecker

class TestMongoDBChecker(TestPlugin):
    def setUp(self):
        self.checker = MongoDBChecker()
        print 'check_mongodb'

    def test_get_connections(self):
        self.assert_status("-t CONNECTIONS")

    def test_get_memory_used(self):
        self.assert_status("-t MEMORY_USED")

    def test_get_insert_rate(self):
        self.assert_status("-t INSERT")

    def test_get_update_rate(self):
        self.assert_status("-t UPDATE")

    def test_get_command_rate(self):
        self.assert_status("-t COMMAND")

    def test_get_query_rate(self):
        self.assert_status("-t QUERY")

    def test_get_delete_rate(self):
        self.assert_status("-t DELETE")

    def test_get_locked_ratio(self):
        self.assert_status("-t LOCKED_PERCENTAGE")

    def test_get_miss_ratio(self):
        self.assert_status("-t MISS_RATIO")

    def test_get_resets(self):
        self.assert_status("-t RESETS")

    def test_get_hits(self):
        self.assert_status("-t HITS")

    def test_get_misses(self):
        self.assert_status("-t MISSES")

    def test_get_accesses(self):
        self.assert_status("-t ACCESSES")

if __name__ == "__main__":
    unittest.main()