'''
Created on May 29, 2012

@author: yangming
@copyright: appfirst inc.
'''

import nagios
import commands

class MySqlChecker(nagios.BaseAnalyst):
    def __init__(self):
        super(MySqlChecker, self).__init__()
        self.parser.add_argument("-t", "--type", type=str, required=True);
        self.parser.add_argument("-u", "--user", type=str, required=False);
        self.parser.add_argument("-p", "--password", type=str, required=False);

    def check(self, request):
        if request.type == 'SLOW_QUERIES':
            return self.get_slow_queries(request)
        if request.type == 'CONNECTIONS':
            return self.get_connections(request)
        if request.type == 'SELECTS':
            return self.get_select_stats(request)
        if request.type == 'TOTAL_BYTES':
            return self.get_select_stats(request)

    def get_slow_queries(self, request):
        attr = "Slow_queries";
        service = request.type
        value = int(self.parse_status_output(attr, request))
        status_code = self.judge(value, request)
        r = nagios.Result(service, status_code, '%s slow queries' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    def get_connections(self, request):
        attr = "Connections";
        service = request.type
        value = int(self.parse_status_output(attr, request))
        status_code = self.judge(value, request)
        r = nagios.Result(service, status_code, '%s connections' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    def get_bytes_transfer(self, request):
        service = request.type
        # read data from command line
        values = []
        values.append(int(self.parse_status_output("Bytes_received", request)))
        values.append(int(self.parse_status_output("Bytes_sent", request)))

        # calculate and judge
        total = 0
        status_code = nagios.Status.OK
        for v in values:
            total += v
            sc = self.judge(v, request)
            if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                status_code = nagios.Status.WARNING
            elif sc == nagios.Status.CRITICAL:
                status_code = nagios.Status.CRITICAL

        # build result
        r = nagios.Result(service, status_code, '%s total bytes' % total);
        r.add_performance_data('total', total, 'B', warn=request.warn, crit=request.crit)
        r.add_performance_data('bytes_received', values[0], 'B', warn=request.warn, crit=request.crit)
        r.add_performance_data('bytes_sent', values[1], 'B', warn=request.warn, crit=request.crit)
        return r

    def get_select_stats(self, request):
        service = request.type
        # read data from command line
        values = []
        values.append(int(self.parse_status_output("Select_full_join", request)))
        values.append(int(self.parse_status_output("Select_full_range_join", request)))
        values.append(int(self.parse_status_output("Select_range", request)))
        values.append(int(self.parse_status_output("Select_range_check", request)))
        values.append(int(self.parse_status_output("Select_scan", request)))

        # calculate and judge
        total = 0
        status_code = nagios.Status.OK
        for v in values:
            total += v
            sc = self.judge(v, request)
            if sc == nagios.Status.WARNING and status_code == nagios.Status.OK:
                status_code = nagios.Status.WARNING
            elif sc == nagios.Status.CRITICAL:
                status_code = nagios.Status.CRITICAL

        # build result
        r = nagios.Result(service, status_code, '%s select' % total);
        r.add_performance_data('total', total, warn=request.warn, crit=request.crit)
        r.add_performance_data('select_full_join', values[0], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_full_range_join', values[1], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_range', values[2], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_range_check', values[3], warn=request.warn, crit=request.crit)
        r.add_performance_data('select_scan', values[4], warn=request.warn, crit=request.crit)
        return r

    def parse_status_output(self, attr, request):
        #stats = {}
        cmd = "mysqladmin"
        if hasattr(request, "user"):
            cmd += " --user=%s" % request.user
        if hasattr(request, "password"):
            cmd += " --password=%s" % request.password
        cmd += " extended-status"
        for l in commands.getoutput(cmd).split('\n')[3:-1]:
            fields = l.split('|')[1:3]
            k = fields[0].strip()
            v = fields[1].strip()
            if attr == k:
                return v
#            stats.setdefault(k, v)
#            try:
#                stats[k] = int(v)
#            except ValueError:
#                try:
#                    stats[k] = float(v)
#                except ValueError:
#                    pass

if __name__ == "__main__":
    MySqlChecker().run()
