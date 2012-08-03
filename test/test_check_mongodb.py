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
        self.assert_status("-t CONNECTIONS -z mongodb_test -d ./status/")

    def test_get_memory_used(self):
        self.assert_status("-t MEMORY_USED -z mongodb_test -d ./status/")

    def test_get_insert_rate(self):
        self.assert_status("-t INSERT -z mongodb_test -d ./status/")

    def test_get_update_rate(self):
        self.assert_status("-t UPDATE -z mongodb_test -d ./status/")

    def test_get_command_rate(self):
        self.assert_status("-t COMMAND -z mongodb_test -d ./status/")

    def test_get_query_rate(self):
        self.assert_status("-t QUERY -z mongodb_test -d ./status/")

    def test_get_delete_rate(self):
        self.assert_status("-t DELETE -z mongodb_test -d ./status/")

    def test_get_locked_ratio(self):
        self.assert_status("-t LOCKED_PERCENTAGE -z mongodb_test -d ./status/")

    def test_get_miss_ratio(self):
        self.assert_status("-t MISS_RATIO -z mongodb_test -d ./status/")

    def test_get_resets(self):
        self.assert_status("-t RESETS -z mongodb_test -d ./status/")

    def test_get_hits(self):
        self.assert_status("-t HITS -z mongodb_test -d ./status/")

    def test_get_misses(self):
        self.assert_status("-t MISSES -z mongodb_test -d ./status/")

    def test_get_accesses(self):
        self.assert_status("-t ACCESSES -z mongodb_test -d ./status/")

if __name__ == "__main__":
    unittest.main()