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
from check_passenger import PassengerChecker

class TestPassengerChecker(TestPlugin):
    def setUp(self):
        self.checker = PassengerChecker()
        try:
            os.mkdir("./status/")
        except OSError:
            pass
        print 'check_passenger'

    def test_get_max_procs(self):
        self.assert_status("-t MAX_PROCESSES -z passenger_test -d ./status/")

    def test_get_procs(self):
        self.assert_status("-t RUNNING_PROCESSES -z passenger_test -d ./status/")

    def test_get_active_procs(self):
        self.assert_status("-t ACTIVE_PROCESSES -z passenger_test -d ./status/")

if __name__ == "__main__":
    unittest.main()