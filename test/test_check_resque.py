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
from check_resque import ResqueChecker

class TestResqueChecker(TestPlugin):
    def setUp(self):
        self.checker = ResqueChecker()
        try:
            os.mkdir("./status/")
        except OSError:
            pass
        print 'check_resque'

    def test_get_connections_active(self):
        self.assert_status("-t QUEUE_LENGTH -z resque_test -d ./status/")

    def test_get_connections_waiting(self):
        self.assert_status("-t JOB_PROCESSED -z resque_test -d ./status/")


if __name__ == "__main__":
    unittest.main()