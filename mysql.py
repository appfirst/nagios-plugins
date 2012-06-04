'''
Created on May 29, 2012

@author: yangming
@copyright: appfirst inc.
'''

import nagios
import commands

class MySqlChecker(nagios.BatchStatusPlugin):
    def __init__(self):
        super(MySqlChecker, self).__init__()
        self.parser.add_argument("-f", "--filename", default='mysql-extended-status', type=str, required=False);
        choices = ["QUERIES_PER_SECOND",
                   "SLOW_QUERIES",
                   "ROW_OPERATIONS",
                   "TRANSACTIONS",
                   "NETWORK_TRAFFIC",
                   "CONNECTIONS",
                   "SELECTS",
                   "TOTAL_BYTES",
                   "REPLICATION"]
        self.parser.add_argument("-t", "--type", choices=choices, required=True);
        self.parser.add_argument("-u", "--user", type=str, required=False);
        self.parser.add_argument("-p", "--password", type=str, required=False);

    def check(self, request):
        self.stats = self.parse_status_output(request)
        if len(self.stats) == 0:
            return nagios.Result(request.type, nagios.Status.CRITICAL,
                                 "cannot connect to mysql.")
        if request.type == 'QUERIES_PER_SECOND':
            r = self.get_queries_per_second(request)
        if request.type == 'SLOW_QUERIES':
            r = self.get_slow_queries(request)
        if request.type == 'ROW_OPERATIONS':
            r = self.get_row_opertions(request)
        if request.type == 'TRANSACTIONS':
            r = self.get_transactions(request)
        if request.type == 'NETWORK_TRAFFIC':
            return nagios.Result(request.type, nagios.Status.UNKNOWN,"mysterious status")
        if request.type == 'CONNECTIONS':
            r = self.get_connections(request)
        if request.type == 'SELECTS':
            r = self.get_select_stats(request)
        if request.type == 'TOTAL_BYTES':
            r = self.get_bytes_transfer(request)
        if request.type == 'REPLICATION':
            return nagios.Result(request.type, nagios.Status.UNKNOWN,"mysterious status")
        return r

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

    def get_queries_per_second(self, request):
        queries = self.get_delta_value("Queries")
        sec = self.get_delta_value("Uptime")
        value = float(queries) / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s queries per second' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    def get_slow_queries(self, request):
        value = self.get_delta_value("Slow_queries")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s slow queries' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

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

    def get_connections(self, request):
        value = self.get_delta_value("Connections")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s new connections' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

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

if __name__ == "__main__":
    MySqlChecker().run()
