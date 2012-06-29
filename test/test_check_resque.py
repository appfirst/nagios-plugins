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
from check_resque import ResqueChecker

class TestResqueChecker(TestPlugin):
    def setUp(self):
        self.checker = ResqueChecker()
        print 'check_resque'

    def test_get_connections_active(self):
        self.assert_status("-t QUEUE_LENGTH")

    def test_get_connections_waiting(self):
        self.assert_status("-t JOB_PROCESSED")


if __name__ == "__main__":
    unittest.main()