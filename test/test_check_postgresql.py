'''
Created on Jun 20, 2012

@author: Yangming
'''
import sys, os
_rootpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(
    os.path.join(_rootpath, ".."))

from test_plugin import TestPlugin
from check_postgresql import PostgresChecker

class TestPostgresChecker(TestPlugin):
    def test_check_postgresql(self):
        self.checker = PostgresChecker()
        print ' - testing: check_postgresql'
        self.assert_status("-u postgres -t TUPLE_READ")
        self.assert_status("-u postgres -t TUPLE_INSERTED")
        self.assert_status("-u postgres -t TUPLE_UPDATED")
        self.assert_status("-u postgres -t TUPLE_DELETED")