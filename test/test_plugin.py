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
import nagios

class TestPlugin(unittest.TestCase):
    def assert_status(self, argument, status_code=nagios.Status.OK):
        # change the standard output to StringIO()
        original_stdout, sys.stdout = sys.stdout, StringIO()
        args = argument.split()
        # get output and exit_code
        exit_code = 0
        try:
            self.checker.run(args)
        except SystemExit as se:
            exit_code = se.code
        output = sys.stdout.getvalue()
        # change the standard output back
        sys.stdout.close()
        sys.stdout = original_stdout
        # print and assert
        print "\targv:   %s" % argument
        print "\tstdout: %s" % output
        self.assertEqual(exit_code, status_code,
                         "return %s, expecting %s" %(
                            nagios.Status.to_status(exit_code),
                            nagios.Status.to_status(status_code)))