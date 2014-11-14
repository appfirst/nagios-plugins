#!/usr/bin/env python

"""
Created on May 29, 2012
@author: Yangming

Updated 2013-08 by Mike Okner
Updated Sept 26, 2014 by Tony Ling
"""

import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd
import argparse


class MySqlChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MySqlChecker, self).__init__(*args, **kwargs)
        # Hack to determine uniqueness of script defs
        check = argparse.ArgumentParser()
        check.add_argument("-H", "--host",     required=False, type=str)
        check.add_argument("-p", "--port",     required=False, type=int)
        chk, unknown = check.parse_known_args()

        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@mysqladmin_extended-status')
        self.parser.add_argument("-u", "--user",     required=False, type=str, default='mysql')
        self.parser.add_argument("-s", "--password", required=False, type=str)
        self.parser.add_argument("-H", "--host",     required=False, type=str)
        self.parser.add_argument("-p", "--port",     required=False, type=int)
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='mysql')
        self.parser.add_argument("--unique",   required=False, type=str, default=str(chk.host)+str(chk.port))

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

    @plugin.command("QCACHE_BLOCK_UTILIZATION")
    @statsd.gauge
    def get_qcache_block_utilization(self, request):
        free = self.get_status_value("Qcache_free_blocks", request)
	total = self.get_status_value("Qcache_total_blocks", request)
	utilized = float(int(total)-int(free))
	if total == 0:
		utilized = 0
	else:
		utilized = utilized/float(int(total))
        return self.get_result(request, utilized, '%s Query cache block percent utilization' % utilized, 'qcache_block_utilization')

    @plugin.command("QCACHE_FREE_BLOCKS")
    @statsd.gauge
    def get_qcache_free_blocks(self, request):
        value = self.get_status_value("Qcache_free_blocks", request)
        return self.get_result(request, value, '%s Query cache free memory blocks' % value, 'qcache_free_blocks')
    
    @plugin.command("QCACHE_TOTAL_BLOCKS")
    @statsd.gauge
    def get_qcache_total_blocks(self, request):
        value = self.get_status_value("Qcache_total_blocks", request)
        return self.get_result(request, value, '%s Query cache total memory blocks' % value, 'qcache_total_blocks')


    @plugin.command("QCACHE_FREE_MEMORY")
    @statsd.gauge
    def get_qcache_free_memory(self, request):
        value = self.get_status_value("Qcache_free_memory", request)
        return self.get_result(request, value, '%s Query cache free memory' % value, 'qcache_free_memory')

    @plugin.command("QCACHE_HITS")
    @statsd.gauge
    def get_qcache_hits(self, request):
        value = self.get_status_value("Qcache_hits", request)
        return self.get_result(request, value, '%s Query cache hits' % value, 'qcache_hits')

    @plugin.command("QCACHE_INSERTS")
    @statsd.gauge
    def get_qcache_inserts(self, request):
        value = self.get_status_value("Qcache_inserts", request)
        return self.get_result(request, value, '%s Queries added to query cache' % value, 'qcache_inserts')

    @plugin.command("QCACHE_QUERIES_IN_CACHE")
    @statsd.gauge
    def get_qcache_queries_in_cache(self, request):
        value = self.get_status_value("Qcache_queries_in_cache", request)
        return self.get_result(request, value, '%s Queries registered in query cache' % value, 'qcache_queries_in_cache')

    @plugin.command("ROW_LOCKS_CURRENT_WAITS")
    @statsd.gauge
    def get_row_locks_current_waits(self, request):
        value = self.get_status_value("Innodb_row_lock_current_waits", request)
        return self.get_result(request, value, '%s Row locks currently being waited for' % value, 'row_locks_curent_waits')

    @plugin.command("ROW_LOCKS_TIME_AVERAGE")
    @statsd.gauge
    def get_row_locks_current_average(self, request):
        value = self.get_status_value("Innodb_row_lock_time_avg", request)
        return self.get_result(request, value, '%s Average time to acquire a row lock (ms)' % value, 'row_locks_time_avg')

    @plugin.command("TABLE_LOCKS_IMMEDIATE")
    @statsd.gauge
    def get_table_locks_immediate(self, request):
        value = self.get_status_value("Table_locks_immediate", request)
        return self.get_result(request, value, '%s Table locks immediately granted' % value, 'Table_locks_immediate')

    @plugin.command("TABLE_LOCKS_WAITED")
    @statsd.gauge
    def get_table_locks_waited(self, request):
        value = self.get_status_value("Table_locks_waited", request)
        return self.get_result(request, value, '%s Table locks waits needed' % value, 'Table_locks_waited')


if __name__ == "__main__":
    import sys
    MySqlChecker().run(sys.argv[1:])
