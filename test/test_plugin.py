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
import time

class TestPlugin(unittest.TestCase):
    def assert_status(self, argument, status_code=nagios.Status.OK):
        # get output and exit_code
        exit_code = 0
        start = time.time()
        try:
            # change the standard output to StringIO()
            sio = StringIO()
            original_stdout, sys.stdout = sys.stdout, sio
            args = argument.split()
            self.checker.run(args)
        except SystemExit as se:
            exit_code = se.code
        finally:
            # change the standard output back
            sys.stdout = original_stdout
            output = sio.getvalue()
            sio.close()
            duration = time.time() - start
            # print and assert
            print "\targv:   %s" % argument
            print "\tstdout: %s" % output.rstrip()
            print "\tran in: %s secs" % duration
        self.assertEqual(exit_code, status_code,
                         "return %s, expecting %s" %(
                            nagios.Status.to_status(exit_code),
                            nagios.Status.to_status(status_code)))