#!/usr/bin/python
'''
Created on Jun 14, 2012

@author: yangming
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd

class PostgresChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(PostgresChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='psql', type=str, required=False);
        self.parser.add_argument("-u", "--user", required=False, type=str);
        self.parser.add_argument("-p", "--password", required=False, type=str);

    @plugin.command("CONNECTIONS_ACTIVE")
    @statsd.gauge("sys.app.postgres.connections_active")
    def get_connections_active(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity " \
                   "WHERE waiting=\'f\' AND current_query<>\'<IDLE>\'"
        value = self._single_value_stat(request, sql_stmt, "%s active conns", "active")
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s active conns" % value);
        r.add_performance_data("active", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("CONNECTIONS_WAITING")
    @statsd.gauge("sys.app.postgres.connections_waiting")
    def get_connections_waiting(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity WHERE waiting=\'t\';"
        value = self._single_value_stat(request, sql_stmt, "%s waiting conns", "waiting")
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s waiting conns" % value);
        r.add_performance_data("waiting", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("CONNECTIONS_IDLE")
    @statsd.gauge("sys.app.postgres.conenctions_idle")
    def get_connections_idle(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity WHERE current_query=\'<IDLE>\';"
        value = self._single_value_stat(request, sql_stmt, "%s idle conns", "idle")
        if value is None:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s idle conns" % value);
        r.add_performance_data("idle", value, warn=request.warn, crit=request.crit)
        return r

    def _single_value_stat(self, request, sql_stmt, msg_pattern, pfname):
        rows = self.run_sql(sql_stmt, request)
        value = None
        if len(rows) > 0 or len(rows[0]) > 0:
            try:
                value = int(rows[0][0])
            except ValueError:
                pass
        return value

    @plugin.command("DATABASE_SIZE")
    @statsd.gauge("sys.app.postgres.database_size")
    def get_database_size(self, request):
        sql_stmt = "SELECT datname, pg_database_size(datname) FROM pg_database;"
        stat, sub_stats = self._stats_by_database(request, sql_stmt)
        # to MB
        value = float(stat)
        value /= 1024 * 1024
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, 'total dbsize: %sMB' % value);
        r.add_performance_data('total', value, UOM='MB', warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            v = float(v)
            v /= 1024 * 1024
            r.add_performance_data(k, v,  warn=request.warn, crit=request.crit)
        return r

    def _stats_by_database(self, request, sql_stmt):
        sub_stats = {}
        rows = self.run_sql(sql_stmt, request)
        for datname, value in rows:
            try:
                value = int(value)
            except ValueError:
                pass
            sub_stats[datname] = value
        if len(sub_stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        stat = reduce(lambda x,y:x+y, sub_stats.itervalues())
        return stat, sub_stats

    @plugin.command("TUPLE_READ")
    @statsd.counter("sys.app.postgres.tuple_fetched")
    def get_tuple_read(self, request):
        statkey = "tup_fetched"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple fetched' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TUPLE_INSERTED")
    @statsd.counter("sys.app.postgres.tuple_inserted")
    def get_tuple_inserted(self, request):
        statkey = "tup_inserted"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple inserted' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TUPLE_UPDATED")
    @statsd.counter("sys.app.postgres.tuple_updated")
    def get_tuple_updated(self, request):
        statkey = "tup_updated"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple updated' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TUPLE_DELETED")
    @statsd.counter("sys.app.postgres.tuple_deleted")
    def get_tuple_deleted(self, request):
        statkey = "tup_deleted"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple deleted' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    def get_delta_value(self, request, statkey, sql_stmt):
        value, sub_stats = self._stats_by_database(request, sql_stmt)

        print sub_stats

        self.laststats = self.retrieve_last_status(request)
        last_sub_stats = self.laststats.setdefault(statkey, [])
        self.laststats[statkey] = sub_stats

        print last_sub_stats

        if len(last_sub_stats):
            last_value = reduce(lambda x,y:x+y, last_sub_stats.itervalues())
            value -= last_value
            for database in sub_stats:
                sub_stats[database] -= last_sub_stats.setdefault(database, 0)
        self.save_status(request)
        return value, sub_stats

    def run_sql(self, sql_stmt, request=None):
        cmd_template = "psql -Atc \"%s\""
        if request:
            if hasattr(request, "user") and request.user is not None:
                cmd_template = "sudo -u %s " % request.user + cmd_template
            if hasattr(request, "password") and request.password is not None:
                cmd_template += " -p %s" % request.password
        cmd = cmd_template % sql_stmt
        output = commands.getoutput(cmd)
        if "command not found" in output:
            return []
        elif "FATAL:  role \"root\" does not exist" in output:
            return []
        return [tuple(row.split('|')) for row in output.split("\n")]

if __name__ == "__main__":
    import sys
    PostgresChecker().run(sys.argv[1:])
