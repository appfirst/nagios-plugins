'''
Created on May 30, 2012

@author: yangming
'''
import unittest
import nagios
import statsd
import sys
from StringIO import StringIO
import mock

class BasePluginMock(nagios.BasePlugin):
    def check(self, request):
        pass

class TestNagios(unittest.TestCase):
    def test_rootify(self):
        mock_os = mock.Mock()
#        sys.modules['os'] = mock_os
        nagios.__dict__['os'] = mock_os
        mock_os.geteuid.return_value = 1
        self.assertEqual("sudo ls",             nagios.rootify("ls"))
        self.assertEqual("sudo ls",             nagios.rootify("sudo ls"))
        self.assertEqual("sudo -u appfirst ls", nagios.rootify("ls", "appfirst"))
        self.assertEqual("sudo -u appfirst ls", nagios.rootify("sudo ls", "appfirst"))
        mock_os.geteuid.return_value = 0
        self.assertEqual("echo \"rosie\"",      nagios.rootify("echo \"rosie\""))
        self.assertEqual("sudo echo \"rosie\"", nagios.rootify("sudo echo \"rosie\""))
        self.assertEqual("su -l appfirst -c \"echo \\\"rosie\\\"\"", 
                                                nagios.rootify("echo \"rosie\"", "appfirst"))


class TestStatsd(unittest.TestCase):
    def statsd_decorator(self, method):
        self.assertTrue(method is not None, "empty method returned")
        return method;

    def test_statsd_gauge(self):
        @self.statsd_decorator
        @statsd.gauge
        def testfunc1(*args, **kwargs):
            result =  nagios.Result("GAUGE_COMMAND", nagios.Status.OK)
            result.add_performance_data("total", 10)
            return result

    def test_statsd_counter(self):
        @self.statsd_decorator
        @statsd.counter
        def testfunc2(*arg, **kwargs):
            result =  nagios.Result("COUNTER_COMMAND", nagios.Status.OK)
            result.add_performance_data("total", 10)
            return result

    def test_statsd_timer(self):
        @self.statsd_decorator
        @statsd.timer
        def testfunc3(*arg, **kwargs):
            result =  nagios.Result("TIMER_COMMAND", nagios.Status.OK)
            result.add_performance_data("total", 10)
            return result

class TestBasePlugin(unittest.TestCase):
    def setUp(self):
        self.original_stdout, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self.original_stdout

    def test_result_str(self):
        # a result w/out pf data
        r = nagios.Result('SLOW_QUERIES', nagios.Status.OK, '2 queries', 'MYSQL')
        expected = 'SLOW_QUERIES OK: 2 queries'
        self.assertEqual(expected, str(r))
        # one performance data added
        r.add_performance_data('slow_queries', 2, warn=10, crit=20)
        expected = 'SLOW_QUERIES OK: 2 queries | slow_queries=2;10;20'
        self.assertEqual(expected, str(r))
        # two performance data added
        r.add_performance_data('slow_queries_rate', 0.2, warn=0.5, crit=1)
        expected = 'SLOW_QUERIES OK: 2 queries | slow_queries=2;10;20 slow_queries_rate=0.2;0.5;1'
        self.assertEqual(expected, str(r))

    def test_verdict(self):
        ba = BasePluginMock()
        self.assertEqual(nagios.Status.OK, ba.verdict(2, 6, 8))
        self.assertEqual(nagios.Status.OK, ba.verdict(2, 5, None))
        self.assertEqual(nagios.Status.OK, ba.verdict(2, None, None))

        self.assertEqual(nagios.Status.OK, ba.verdict(2, 6, 8))
        self.assertEqual(nagios.Status.WARNING, ba.verdict(7, 6, 8))
        self.assertEqual(nagios.Status.CRITICAL, ba.verdict(9, 6, 8))

        self.assertEqual(nagios.Status.WARNING, ba.verdict(8, 6, 8, False,  True))
        self.assertEqual(nagios.Status.CRITICAL, ba.verdict(8, 6, 8, False,  False))

        self.assertEqual(nagios.Status.CRITICAL, ba.verdict(3, 8, 6, True, False))
        self.assertEqual(nagios.Status.WARNING, ba.verdict(7, 8, 6, True, False))
        self.assertEqual(nagios.Status.OK, ba.verdict(9, 8, 6, True, False))

        self.assertEqual(nagios.Status.CRITICAL, ba.verdict(6, 8, 6, True, False))
        self.assertEqual(nagios.Status.WARNING, ba.verdict(6, 8, 6, True, True))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()
