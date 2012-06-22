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

#import nagios
#nagios.CommandBasedPlugin.commandmap = {}

class TestMongoDBChecker(TestPlugin):
    def setUp(self):
        self.checker = MongoDBChecker()
        print 'check_mongodb'

    def test_get_connections(self):
        self.assert_status("-t CONNECTIONS")

    def test_get_memory_used(self):
        self.assert_status("-t MEMORY_USED")

    def test_get_insert_rate(self):
        self.assert_status("-t INSERT_RATE")

    def test_get_update_rate(self):
        self.assert_status("-t UPDATE_RATE")

    def test_get_command_rate(self):
        self.assert_status("-t COMMAND_RATE")

    def test_get_query_rate(self):
        self.assert_status("-t QUERY_RATE")

    def test_get_delete_rate(self):
        self.assert_status("-t DELETE_RATE")

    def test_get_locked_ratio(self):
        self.assert_status("-t LOCKED_PERCENTAGE")

    def test_get_miss_ratio(self):
        self.assert_status("-t MISS_PERCENTAGE")

if __name__ == "__main__":
    unittest.main()