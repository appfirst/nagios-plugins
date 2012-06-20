'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys, os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, ".."))

from test_plugin import TestPlugin
from check_passenger import PassengerChecker

class TestPassengerChecker(TestPlugin):
    def test_check_passenger(self):
        self.checker = PassengerChecker()
        print ' - testing: check_passenger'
        self.assert_status("-t MAX_PROCESSES")
        self.assert_status("-t RUNNING_PROCESSES")
        self.assert_status("-t ACTIVE_PROCESSES")
