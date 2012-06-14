#!/usr/bin/python
'''
Created on May 29, 2012

@author: yangming
@copyright: appfirst inc.
'''

import nagios
from nagios import BatchStatusPlugin
import commands

class MySqlChecker(BatchStatusPlugin):
    def __init__(self):
        super(MySqlChecker, self).__init__()
        self.parser.add_argument("-f", "--filename", default='mysqladmin_extended-status', type=str, required=False);
        self.parser.add_argument("-u", "--user", required=False, type=str);
        self.parser.add_argument("-p", "--password", required=False, type=str);

    def parse_status_output(self, request):
        stats = {}
        cmd = "mysqladmin"
        if hasattr(request, "user") and request.user is not None:
            cmd += " --user=%s" % request.user
        if hasattr(request, "password") and request.password is not None:
            cmd += " --password=%s" % request.password
        cmd += " extended-status"
        for l in commands.getoutput(cmd).split('\n')[3:-1]:
            fields = l.split('|')[1:3]
            k = fields[0].strip()
            v = fields[1].strip()
            stats.setdefault(k, v)
            try:
                stats[k] = int(v)
            except ValueError:
                try:
                    stats[k] = float(v)
                except ValueError:
                    pass
        return stats

    @BatchStatusPlugin.command("QUERIES_PER_SECOND", "cumulative")
    def get_queries_per_second(self, request):
        queries = self.get_delta_value("Queries")
        sec = self.get_delta_value("Uptime")
        value = float(queries) / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s queries per second' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("SLOW_QUERIES", "cumulative")
    def get_slow_queries(self, request):
        value = self.get_delta_value("Slow_queries")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s slow queries' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("ROW_OPERATIONS", "cumulative")
    def get_row_opertions(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Innodb_rows_deleted","Innodb_rows_inserted",
                 "Innodb_rows_updated","Innodb_rows_read"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = self.get_delta_value(attr)
            values.append(v)
            total += v
            sc = self.verdict(v, request)
            if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                status_code = nagios.Status.WARNING
            elif sc == nagios.Status.CRITICAL:
                status_code = nagios.Status.CRITICAL

        # build result
        r = nagios.Result(request.type, status_code, '%s row operations' % total);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_deleted', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_inserted',values[1], warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_updated', values[2], warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_read',    values[3], warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TRANSACTIONS", "cumulative")
    def get_transactions(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Handler_commit","Handler_rollback"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = self.get_delta_value(attr)
            values.append(v)
            total += v
            sc = self.verdict(v, request)
            if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                status_code = nagios.Status.WARNING
            elif sc == nagios.Status.CRITICAL:
                status_code = nagios.Status.CRITICAL

        # build result
        r = nagios.Result(request.type, status_code, '%s transactions' % total);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('commit', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('rollback',values[1], warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("NETWORK_TRAFFIC")
    def get_network_traffic(self, request):
        return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

    @BatchStatusPlugin.command("CONNECTIONS", "cumulative")
    def get_connections(self, request):
        value = self.get_delta_value("Connections")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s new connections' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TOTAL_BYTES", "cumulative")
    def get_bytes_transfer(self, request):
        service = request.type
        # read data from command line, calculate and verdict
        attrs = ["Bytes_received", "Bytes_sent"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = float(self.get_delta_value(attr)) / 1024 /1024
            values.append(v)
            total += v
            sc = self.verdict(v, request)
            if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                status_code = nagios.Status.WARNING
            elif sc == nagios.Status.CRITICAL:
                status_code = nagios.Status.CRITICAL

        # build result
        r = nagios.Result(service, status_code, '%sMB in total' % total);
        r.add_performance_data('total', total, 'MB', warn=request.warn, crit=request.crit)
        r.add_performance_data('bytes_received', values[0], 'MB', warn=request.warn, crit=request.crit)
        r.add_performance_data('bytes_sent', values[1], 'MB', warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("SELECTS", "cumulative")
    def get_select_stats(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Select_full_join",  "Select_full_range_join","Select_range",
                 "Select_range_check","Select_scan"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = self.get_delta_value(attr)
            values.append(v)
            total += v
            sc = self.verdict(v, request)
            if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                status_code = nagios.Status.WARNING
            elif sc == nagios.Status.CRITICAL:
                status_code = nagios.Status.CRITICAL

        # build result
        r = nagios.Result(request.type, status_code, '%s select' % total);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('select_full_join', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_full_range_join', values[1], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_range', values[2], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_range_check', values[3], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_scan', values[4], warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("REPLICATION")
    def get_replication(self, request):
        return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

if __name__ == "__main__":
    MySqlChecker().run()
