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

    def get_slow_queries(self, request):
        attr = "Slow_queries";
        service = request.type
        value = int(self.parse_status_output(request, attr))
        status_code = self.judge(value, request)
        r = nagios.Result(service, status_code, '%s slow queries' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    def get_connections(self, request):
        attr = "Connections";
        service = request.type
        value = int(self.parse_status_output(request, attr))
        status_code = self.judge(value, request)
        r = nagios.Result(service, status_code, '%s connections' % value);
        r.add_performance_data('total', value, warn=request.warn, crit=request.crit)
        return r

    def parse_status_output(self, request, attr):
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
