#!/usr/bin/python
'''
Created on Jun 14, 2012

@author: yangming
'''
import nagios
from nagios import BatchStatusPlugin
import commands

class PostgresChecker(BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(PostgresChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='psql', type=str, required=False);

    #TODO: replace all with "psql -c 'select * from pg_stat_database' -A" 

    def retreive_current_status(self, request, colname):
        sql_stmt = "select datname, %s from pg_stat_database;" % colname
        sub_stats = {}
        rows = self.run_sql(sql_stmt)
        if len(rows):
            return sub_stats
        for datname, value in rows:
            try:
                value = int(value)
            except ValueError:
                pass
            sub_stats[datname] = value
        return sub_stats

    @BatchStatusPlugin.command("TUPLE_READ")
    def get_tuple_read(self, request):
        sub_stats = self.retreive_current_status(request, "tup_fetched")
        if len(sub_stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        value = reduce(lambda x,y:x+y, sub_stats.itervalues())
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple fetched' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TUPLE_INSERTED")
    def get_tuple_inserted(self, request):
        sub_stats = self.retreive_current_status(request, "tup_inserted")
        if len(sub_stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        value = reduce(lambda x,y:x+y, sub_stats.itervalues())
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple inserted' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TUPLE_UPDATED")
    def get_tuple_updated(self, request):
        sub_stats = self.retreive_current_status(request, "tup_updated")
        if len(sub_stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        value = reduce(lambda x,y:x+y, sub_stats.itervalues())
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple updated' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TUPLE_DELETED")
    def get_tuple_deleted(self, request):
        sub_stats = self.retreive_current_status(request, "tup_deleted")
        if len(sub_stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                "failed to check postgres. check arguments and try again.")
        value = reduce(lambda x,y:x+y, sub_stats.itervalues())
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple deleted' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        for k, v in sub_stats.iteritems():
            r.add_performance_data(k, v, warn=request.warn, crit=request.crit)
        return r

    def run_sql(self, sql_stmt):
        cmd_template = "psql -c \'%s\' -A -t"
        cmd = cmd_template % sql_stmt
        output = commands.getoutput(cmd)
        if "command not found" in output:
            return []
        elif "FATAL:  role \"root\" does not exist" in output:
            return []
        elif "|" not in output:
            return []
        return [row.split('|') for row in output.split("\n")]

if __name__ == "__main__":
    import sys
    PostgresChecker().run(sys.argv[1:])
