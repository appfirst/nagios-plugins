#!/usr/bin/env python

"""
Created on Aug 8, 2013

@author: Mike Okner

Split from the check_postgresql.py script because PostgreSQL 9.2 has some
changes to the pg_stat_activity table that aren't backwards compatible.
"""

import commands
import statsd
import nagios
from nagios import CommandBasedPlugin as plugin

class PostgresChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(PostgresChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@stats_psql')
        self.parser.add_argument("-u", "--user",     required=False, type=str, default='postgres')
        self.parser.add_argument("-p", "--port",     required=False, type=int)
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='postgres')

    @plugin.command("CONNECTIONS_ACTIVE")
    @statsd.gauge
    def get_connections_active(self, request):
        sql_stmt = """SELECT count(*) FROM pg_stat_activity
                   WHERE waiting = false AND state = \'active\';"""
        value = self._single_value_stat(request, sql_stmt)
        return self.get_result(request, value, '%s active conns' % value, 'active')

    @plugin.command("CONNECTIONS_WAITING")
    @statsd.gauge
    def get_connections_waiting(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity WHERE waiting = true;"
        value = self._single_value_stat(request, sql_stmt)
        return self.get_result(request, value, '%s waiting conns' % value, 'waiting')

    @plugin.command("CONNECTIONS_IDLE")
    @statsd.gauge
    def get_connections_idle(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity WHERE state LIKE \'%idle\';"
        value = self._single_value_stat(request, sql_stmt)
        return self.get_result(request, value, '%s idle conns' % value, 'idle')

    def _single_value_stat(self, request, query):
        rows = self.run_query(request, query)
        if len(rows) > 0 or len(rows[0]) > 0:
            value = nagios.to_num(rows[0][0])
            if value is None:
                raise nagios.OutputFormatError(request, rows)
            return value
        else:
            raise nagios.StatusUnknownError(request.option)

    @plugin.command("DATABASE_SIZE")
    @statsd.gauge
    def get_database_size(self, request):
        sql_stmt = "SELECT datname, pg_database_size(datname) FROM pg_database;"
        stat, sub_stats = self._multi_value_stats(request, sql_stmt)
        # to MB
        value = nagios.BtoMB(stat)
        for k, v in sub_stats.iteritems():
            sub_stats[k] = nagios.BtoMB(v)
        return self.get_result(request, value,
                    'total dbsize: %sMB' % value, 'total', UOM='MB', sub_perfs=sub_stats.iteritems())

    @plugin.command("LOCKS_ACCESS")
    @statsd.gauge
    def get_locks_access(self, request):
        statkey = "access"
        sql_stmt = """SELECT mode, count(*) FROM pg_locks
                   GROUP BY mode HAVING mode ILIKE \'%%%s%%\';""" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        return self.get_result(request, value,
                    '%s locks access' % value, 'total', sub_perfs=sub_stats.iteritems())

    @plugin.command("LOCKS_ROW")
    @statsd.gauge
    def get_locks_row(self, request):
        statkey = "row"
        sql_stmt = """SELECT mode, count(*) FROM pg_locks
                   GROUP BY mode HAVING mode ILIKE \'%%%s%%\';""" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        return self.get_result(request, value,
                    '%s locks row' % value, 'total', sub_perfs=sub_stats.iteritems())

    @plugin.command("LOCKS_SHARE")
    @statsd.gauge
    def get_locks_share(self, request):
        statkey = "share"
        sql_stmt = """SELECT mode, count(*) FROM pg_locks
                   GROUP BY mode HAVING mode ILIKE \'%%%s%%\';""" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        return self.get_result(request, value,
                    '%s locks share' % value, 'total', sub_perfs=sub_stats.iteritems())

    @plugin.command("LOCKS_EXCLUSIVE")
    @statsd.gauge
    def get_locks_exclusive(self, request):
        statkey = "exclusive"
        sql_stmt = """SELECT mode, count(*) FROM pg_locks
                   GROUP BY mode HAVING mode ILIKE \'%%%s%%\';""" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        return self.get_result(request, value,
                    '%s locks exclusive' % value, 'total', sub_perfs=sub_stats.iteritems())

    def _multi_value_stats(self, request, query):
        sub_stats = {}
        rows = self.run_query(request, query)
        for substatname, value in rows:
            value = nagios.to_num(value)
            if value is None:
                raise nagios.OutputFormatError(request, rows)
            sub_stats[substatname] = value
        stat = reduce(lambda x,y:x+y, sub_stats.itervalues(), 0)
        return stat, sub_stats

    @plugin.command("TUPLES_READ")
    @statsd.counter
    def get_tuples_read(self, request):
        statkey = "tup_fetched"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(statkey, request, sql_stmt)
        return self.get_result(request, value,
                    '%s tuples fetched' % value, 'total', sub_perfs=sub_stats.iteritems())

    @plugin.command("TUPLES_INSERTED")
    @statsd.counter
    def get_tuples_inserted(self, request):
        statkey = "tup_inserted"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(statkey, request, sql_stmt)
        return self.get_result(request, value,
                    '%s tuples inserted' % value, 'total', sub_perfs=sub_stats.iteritems())

    @plugin.command("TUPLES_UPDATED")
    @statsd.counter
    def get_tuples_updated(self, request):
        statkey = "tup_updated"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(statkey, request, sql_stmt)
        return self.get_result(request, value,
                    '%s tuples updated' % value, 'total', sub_perfs=sub_stats.iteritems())

    @plugin.command("TUPLES_DELETED")
    @statsd.counter
    def get_tuples_deleted(self, request):
        statkey = "tup_deleted"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(statkey, request, sql_stmt)
        return self.get_result(request, value,
                    '%s tuples deleted' % value, 'total', sub_perfs=sub_stats.iteritems())

    def get_delta_value(self, statkey, request, sql_stmt):
        value, sub_stats = self._multi_value_stats(request, sql_stmt)

        laststats = self.retrieve_last_status(request)
        last_sub_stats = laststats.setdefault(statkey, [])
        laststats[statkey] = sub_stats
        self.save_status(request, laststats)

        if len(last_sub_stats):
            last_value = reduce(lambda x,y:x+y, last_sub_stats.itervalues())
            value -= last_value
            for database in sub_stats:
                sub_stats[database] -= last_sub_stats.setdefault(database, 0)
        return value, sub_stats

    def run_query(self, request, query):
        output = self._get_query_status(query, request)
        if self._validate_output(request, output):
            return [tuple(row.split('|')) for row in output.split("\n")]
        else:
            return []

    def _get_query_status(self, query, request):
        cmd_template = "psql"
        if request.port is not None:
            cmd_template += " -p %s" % request.port
        cmd_template += " -wAtc \"%s\""
        cmd = cmd_template % query
        if request.user:
            cmd = nagios.rootify(cmd, request.user)
        return commands.getoutput(cmd)

    def _validate_output(self, request, output):
        if ("command not found" in output or
            "psql: could not connect to server" in output):
            raise nagios.ServiceInaccessibleError(request, output)
        elif (("psql: FATAL:  role" in output and "does not exist" in output) or
              "psql: fe_sendauth: no password supplied" in output):
            raise nagios.AuthenticationFailedError(request, output)
        elif "does not exist" in output or "psql:" in output:
            raise nagios.OutputFormatError(request, output)
        elif output.strip() == "":
            return False
        return True

if __name__ == "__main__":
    import sys
    PostgresChecker().run(sys.argv[1:])
