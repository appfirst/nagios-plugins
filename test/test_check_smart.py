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
from check_smart import SmartChecker

class TestSmartChecker(TestPlugin):
    def setUp(self):
        self.checker = SmartChecker()
        try:
            os.mkdir("./status/")
        except OSError:
            pass
        print 'check_smart'

    def test_get_overall_health(self):
        self.print_status("-t OVERALL_HEALTH -d ./status/")

    def test_get_adapatec_health(self):
        self.print_status("-t ADAPTEC_HEALTH -d ./status/")

    def test_get_connections_active(self):
        self.print_status("-t REALLOCATE_SECTOR_COUNT -d ./status/")

    def test_get_spin_retry_count(self):
        self.print_status("-t SPIN_RETRY_COUNT -d ./status/")

    def test_get_offline_uncorrectable(self):
        self.print_status("-t OFFLINE_UNCORRECTABLE -d ./status/")

    def test_get_cur_pending_sector(self):
        self.print_status("-t CUR_PENDING_SECTOR -d ./status/")

    def test_get_reallocated_event_count(self):
        self.print_status("-t REALLOCATED_EVENT_COUNT -d ./status/")

    def test_get_spin_up_time(self):
        self.print_status("-t SPIN_UP_TIME -d ./status/")

    def test_get_raw_read_error_rate(self):
        self.print_status("-t RAW_READ_ERROR_RATE -d ./status/")

if __name__ == "__main__":
    unittest.main()