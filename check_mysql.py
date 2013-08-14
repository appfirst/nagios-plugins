#!/usr/bin/env python

"""
Created on May 29, 2012
@author: Yangming

Updated 2013-08 by Mike Okner
"""

import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd


class MySqlChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MySqlChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@mysqladmin_extended-status')
        self.parser.add_argument("-u", "--user",     required=False, type=str, default='mysql')
        self.parser.add_argument("-s", "--password", required=False, type=str)
        self.parser.add_argument("-H", "--host",     required=False, type=str)
        self.parser.add_argument("-p", "--port",     required=False, type=int)
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='mysql')

    def _get_batch_status(self, request):
        cmd = "mysqladmin"
        if hasattr(request, "user") and request.user is not None:
            cmd += " --user=%s" % request.user
        if hasattr(request, "password") and request.password is not None:
            cmd += " --password=%s" % request.password
        if hasattr(request, "host") and request.host is not None:
            cmd += " --host=%s" % request.host
        if hasattr(request, "port") and request.port is not None:
            cmd += " --port=%s" % request.port
        cmd += " extended-status"
        return commands.getoutput(cmd)

    def _parse_output(self, request, output):
        for l in output.split('\n')[3:-1]:
            fields = l.split('|')[1:3]
            k = fields[0].strip()
            v = fields[1].strip()
            value = nagios.to_num(v)
            if value is not None:
                yield k, value

    def _validate_output(self, request, output):
        if "command not found" in output or \
            "Can't connect to MySQL server on" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "Access denied for user" in output:
            raise nagios.AuthenticationFailedError(request, output)
        elif "mysqladmin: connect to server at" in output:
            raise nagios.OutputFormatError(request, output)
        elif output.strip() == "":
            return False
        return True

    @plugin.command("QUERIES_PER_SECOND")
    @statsd.gauge
    def get_queries_per_second(self, request):
        queries = self.get_delta_value("Queries", request)
        sec = self.get_delta_value("Uptime", request)
        value = float(queries) / sec
        return self.get_result(request, value, '%s queries per second' % value, 'total')

    @plugin.command("SLOW_QUERIES")
    @statsd.counter
    def get_slow_queries(self, request):
        value = self.get_delta_value("Slow_queries", request)
        return self.get_result(request, value, '%s slow queries' % value, 'total')

    @plugin.command("ROW_OPERATIONS")
    @statsd.counter
    def get_row_opertions(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Innodb_rows_deleted","Innodb_rows_inserted",
                 "Innodb_rows_updated","Innodb_rows_read"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = self.get_delta_value(attr, request)
            values.append(v)
            total += v
            status_code = self.superimpose(status_code, v, request.warn, request.crit)

        # build result
        r = nagios.Result(request.option, status_code, '%s row operations' % total, request.appname);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_deleted', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_inserted',values[1], warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_updated', values[2], warn=request.warn, crit=request.crit)
        r.add_performance_data('rows_read',    values[3], warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TRANSACTIONS")
    @statsd.counter
    def get_transactions(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Handler_commit","Handler_rollback"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = self.get_delta_value(attr, request)
            values.append(v)
            total += v
            status_code = self.superimpose(status_code, v, request.warn, request.crit)

        # build result
        r = nagios.Result(request.option, status_code, '%s transactions' % total, request.appname);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('commit', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('rollback',values[1], warn=request.warn, crit=request.crit)
        return r

    @plugin.command("NETWORK_TRAFFIC")
    @statsd.counter
    def get_network_traffic(self, request):
        return nagios.Result(request.option, nagios.Status.UNKNOWN,
                                 "mysterious status", request.appname)

    @plugin.command("CONNECTIONS")
    @statsd.counter
    def get_connections(self, request):
        value = self.get_status_value("Threads_connected", request)
        delta = self.get_delta_value("Threads_connected", request)
        return self.get_result(request, value, '%s connections (%s new)' % (value, delta), 'conns')

    @plugin.command("TOTAL_BYTES")
    @statsd.counter
    def get_bytes_transfer(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Bytes_received", "Bytes_sent"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = float(self.get_delta_value(attr, request)) / 1024 /1024
            values.append(v)
            total += v
            status_code = self.superimpose(status_code, v, request.warn, request.crit)

        # build result
        r = nagios.Result(request.option, status_code, '%sMB in total' % total, request.appname);
        r.add_performance_data('total', total, 'MB', warn=request.warn, crit=request.crit)
        r.add_performance_data('bytes_received', values[0], 'MB', warn=request.warn, crit=request.crit)
        r.add_performance_data('bytes_sent', values[1], 'MB', warn=request.warn, crit=request.crit)
        return r

    @plugin.command("SELECTS")  # TODO Deprecate. Should be called something like JOINS
    @statsd.counter
    def get_select_stats(self, request):
        # read data from command line, calculate and verdict
        attrs = ["Select_full_join",  "Select_full_range_join","Select_range",
                 "Select_range_check","Select_scan"]
        values = []
        total = 0
        status_code = nagios.Status.OK
        for attr in attrs:
            v = self.get_delta_value(attr, request)
            values.append(v)
            total += v
            status_code = self.superimpose(status_code, v, request.warn, request.crit)

        # build result
        r = nagios.Result(request.option, status_code, '%s joins' % total, request.appname);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('select_full_join', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_full_range_join', values[1], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_range', values[2], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_range_check', values[3], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_scan', values[4], warn=request.warn, crit=request.crit)
        return r

    @plugin.command("REPLICATION")
    @statsd.gauge
    def get_replication(self, request):
        return nagios.Result(request.option, nagios.Status.UNKNOWN,
                                 "mysterious status", request.appname)

    @plugin.command("QUERIES")
    @statsd.gauge
    def get_queries(self, request):
        value = self.get_delta_value("Queries", request)
        return self.get_result(request, value, '%s queries' % value, 'total')


if __name__ == "__main__":
    import sys
    MySqlChecker().run(sys.argv[1:])
