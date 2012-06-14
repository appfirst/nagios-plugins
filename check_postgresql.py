#!/usr/bin/python
'''
Created on Jun 14, 2012

@author: yangming
@copyright: appfirst inc.
'''

import nagios
from nagios import BatchStatusPlugin
import commands

class PostgresChecker(BatchStatusPlugin):
    def __init__(self):
        super(PostgresChecker, self).__init__()
        self.parser.add_argument("-f", "--filename", default='redis-cli_info', type=str, required=False);

    #TODO: replace all with "psql -c 'select * from pg_stat_database' -A" 

    @BatchStatusPlugin.command("TUPLE_READ")
    def get_tuple_read(self, request):
        sql_stmt = "select datid, datname, tup_fetched from pg_stat_database"
        oids = self.run_sql(sql_stmt)
        value = 0
        for oid in oids:
            sql_stmt = "select * from pg_stat_get_tuples_fetched(%s)" % oid
            row = self.run_sql(sql_stmt)[0]
            try:
                value += int(row)
            except ValueError:
                return nagios.Result(request.type,nagios.Status.UNKNOWN,
                                     "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple fetched' % value);
        r.add_performance_data('tuple_fetched', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TUPLE_INSERTED")
    def get_tuple_inserted(self, request):
        sql_stmt = "select oid from pg_database"
        oids = self.run_sql(sql_stmt)
        value = 0
        for oid in oids:
            sql_stmt = "select * from pg_stat_get_tuples_inserted(%s)" % oid
            row = self.run_sql(sql_stmt)[0]
            try:
                value += int(row)
            except ValueError:
                return nagios.Result(request.type,nagios.Status.UNKNOWN,
                                     "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple inserted' % value);
        r.add_performance_data('tuple_inserted', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TUPLE_UPDATED")
    def get_tuple_updated(self, request):
        sql_stmt = "select oid from pg_database"
        oids = self.run_sql(sql_stmt)
        value = 0
        for oid in oids:
            sql_stmt = "select * from pg_stat_get_tuples_updated(%s)" % oid
            row = self.run_sql(sql_stmt)[0]
            try:
                value += int(row)
            except ValueError:
                return nagios.Result(request.type,nagios.Status.UNKNOWN,
                                     "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple updated' % value);
        r.add_performance_data('tuple_updated', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TUPLE_DELETED")
    def get_tuple_deleted(self, request):
        sql_stmt = "select oid from pg_database"
        oids = self.run_sql(sql_stmt)
        value = 0
        for oid in oids:
            sql_stmt = "select * from pg_stat_get_tuples_deleted(%s)" % oid
            row = self.run_sql(sql_stmt)[0]
            try:
                value += int(row)
            except ValueError:
                return nagios.Result(request.type,nagios.Status.UNKNOWN,
                                     "failed to check postgres. check arguments and try again.")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s tuple deleted' % value);
        r.add_performance_data('tuple_deleted', value, warn=request.warn, crit=request.crit)
        return r

    def run_sql(self, sql_stmt):
        cmd_template = "psql -c \'%s\' -A -t"
        cmd = cmd_template % sql_stmt
        output = commands.getoutput(cmd)
        return [row.split('|') for row in output.split("\n")]

if __name__ == "__main__":
    PostgresChecker().run()
