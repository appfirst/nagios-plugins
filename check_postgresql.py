#!/usr/bin/env python
'''
Created on Jun 14, 2012

@author: Yangming
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd
from service_exception import StatusUnknown, ServiceInaccessible,\
    AuthenticationFailed

class PostgresChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(PostgresChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='psql', type=str, required=False)
        self.parser.add_argument("-u", "--user", required=False, type=str)
        self.parser.add_argument("-p", "--password", required=False, type=str)

    @plugin.command("CONNECTIONS_ACTIVE")
    @statsd.gauge("sys.app.postgres.connections_active")
    def get_connections_active(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity " \
                   "WHERE waiting=\'f\' AND current_query<>\'<IDLE>\'"
        value = self._single_value_stat(request, sql_stmt)
        if value is None:
            raise StatusUnknown(request.type)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s active conns" % value);
        r.add_performance_data("active", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("CONNECTIONS_WAITING")
    @statsd.gauge("sys.app.postgres.connections_waiting")
    def get_connections_waiting(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity WHERE waiting=\'t\';"
        value = self._single_value_stat(request, sql_stmt)
        if value is None:
            raise StatusUnknown(request.type)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s waiting conns" % value);
        r.add_performance_data("waiting", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("CONNECTIONS_IDLE")
    @statsd.gauge("sys.app.postgres.conenctions_idle")
    def get_connections_idle(self, request):
        sql_stmt = "SELECT count(*) FROM pg_stat_activity WHERE current_query=\'<IDLE>\';"
        value = self._single_value_stat(request, sql_stmt)
        if value is None:
            raise StatusUnknown(request.type)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s idle conns" % value);
        r.add_performance_data("idle", value, warn=request.warn, crit=request.crit)
        return r

    def _single_value_stat(self, request, sql_stmt):
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
        stat, sub_stats = self._multi_value_stats(request, sql_stmt)
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

    @plugin.command("LOCKS_ACCESS")
    @statsd.gauge("sys.app.postgres.locks_access")
    def get_locks_access(self, request):
        statkey = "access"
        sql_stmt = "SELECT mode, count(*) " \
                   "FROM pg_locks " \
                   "GROUP BY mode " \
                   "HAVING mode ILIKE \'%%%s%%\';" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s locks access' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("LOCKS_ROW")
    @statsd.gauge("sys.app.postgres.locks_row")
    def get_locks_row(self, request):
        statkey = "row"
        sql_stmt = "SELECT mode, count(*) " \
                   "FROM pg_locks " \
                   "GROUP BY mode " \
                   "HAVING mode ILIKE \'%%%s%%\';" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s locks row' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("LOCKS_SHARE")
    @statsd.gauge("sys.app.postgres.locks_share")
    def get_locks_share(self, request):
        statkey = "share"
        sql_stmt = "SELECT mode, count(*) " \
                   "FROM pg_locks " \
                   "GROUP BY mode " \
                   "HAVING mode ILIKE \'%%%s%%\';" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s locks share' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("LOCKS_EXCLUSIVE")
    @statsd.gauge("sys.app.postgres.locks_exclusive")
    def get_locks_exclusive(self, request):
        statkey = "exclusive"
        sql_stmt = "SELECT mode, count(*) " \
                   "FROM pg_locks " \
                   "GROUP BY mode " \
                   "HAVING mode ILIKE \'%%%s%%\';" % statkey
        value, sub_stats = self._multi_value_stats(request, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s locks exclusive' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    def _multi_value_stats(self, request, sql_stmt):
        stat = 0
        sub_stats = {}
        rows = self.run_sql(sql_stmt, request)
        #if len(rows) == 0:
        #    return 0, sub_stats
        for substatname, value in rows:
            try:
                value = int(value)
            except ValueError:
                pass
            sub_stats[substatname] = value
        if len(sub_stats) > 0:
            stat = reduce(lambda x,y:x+y, sub_stats.itervalues())
        return stat, sub_stats

    @plugin.command("TUPLES_READ")
    @statsd.counter("sys.app.postgres.tuples_fetched")
    def get_tuples_read(self, request):
        statkey = "tup_fetched"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuples fetched' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TUPLES_INSERTED")
    @statsd.counter("sys.app.postgres.tuples_inserted")
    def get_tuples_inserted(self, request):
        statkey = "tup_inserted"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuples inserted' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TUPLES_UPDATED")
    @statsd.counter("sys.app.postgres.tuples_updated")
    def get_tuples_updated(self, request):
        statkey = "tup_updated"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuples updated' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TUPLES_DELETED")
    @statsd.counter("sys.app.postgres.tuples_deleted")
    def get_tuples_deleted(self, request):
        statkey = "tup_deleted"
        sql_stmt = "SELECT datname, %s FROM pg_stat_database;" % statkey
        value, sub_stats = self.get_delta_value(request, statkey, sql_stmt)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuples deleted' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    def get_delta_value(self, request, statkey, sql_stmt):
        value, sub_stats = self._multi_value_stats(request, sql_stmt)

        self.laststats = self.retrieve_last_status(request)
        last_sub_stats = self.laststats.setdefault(statkey, [])
        self.laststats[statkey] = sub_stats

        if len(last_sub_stats):
            last_value = reduce(lambda x,y:x+y, last_sub_stats.itervalues())
            value -= last_value
            for database in sub_stats:
                sub_stats[database] -= last_sub_stats.setdefault(database, 0)
        self.save_status(request)
        return value, sub_stats

    def run_sql(self, sql_stmt, request):
        cmd_template = "psql"
        if hasattr(request, "user") and request.user is not None:
            cmd_template = "sudo -u %s " % request.user + cmd_template
        if hasattr(request, "password") and request.password is not None:
            cmd_template += " -p %s" % request.password
        cmd_template += " -Atc \"%s\""
        cmd = cmd_template % sql_stmt
        output = commands.getoutput(cmd)
        if self.validate_output(request, output):
            return [tuple(row.split('|')) for row in output.split("\n")]
        else:
            return []

    def validate_output(self, request, output):
        if "command not found" in output:
            raise ServiceInaccessible(request, output)
        elif "psql: could not connect to server" in output:
            raise ServiceInaccessible(request, output)
        elif "FATAL:  role" in output and "does not exist" in output:
            raise AuthenticationFailed(request, output)
        elif output.strip() == "":
            return False
        return True

if __name__ == "__main__":
    import sys
    PostgresChecker().run(sys.argv[1:])
