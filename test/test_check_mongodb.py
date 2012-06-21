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

class TestMongoDBChecker(TestPlugin):
    def setUp(self):
        pass

if __name__ == "__main__":
    unittest.main()