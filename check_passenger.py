#!/usr/bin/env python
'''
Created on Jun 7, 2012

@author: yangming
@copyright: appfirst inc.
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd

class PassengerChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(PassengerChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str,
                                 default="passenger-status");

    def retrieve_current_status(self, request):
        stats = {}
        # TODO: make sudo and path optional
        cmd = "sudo /usr/bin/passenger-status"
        output = commands.getoutput(cmd)
        if "ERROR" in output:
            return stats
        for l in output.split('\n'):
            pair = l.split('=')
            if len(pair) == 2:
                k = pair[0].strip()
                v = pair[1].strip()
                try:
                    stats[k] = int(v)
                except ValueError:
                    try:
                        stats[k] = float(v)
                    except ValueError:
                        stats[k] = v
        return stats

    @plugin.command("RUNNING_PROCESSES", nagios.BatchStatusPlugin.status)
    @statsd.gauge("sys.app.passenger.max_processes")
    def get_procs(self, request):
        value = self.stats["count"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s running processes" % value);
        r.add_performance_data("running_procs", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MAX_PROCESSES", nagios.BatchStatusPlugin.status)
    @statsd.gauge("sys.app.passenger.running_processes")
    def get_max_procs(self, request):
        value = self.stats["max"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s max processes" % value);
        r.add_performance_data("max", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("ACTIVE_PROCESSES", nagios.BatchStatusPlugin.status)
    @statsd.gauge("sys.app.passenger.active_processes")
    def get_active_procs(self, request):
        value = self.stats["active"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s active processes" % value);
        r.add_performance_data("active", value, warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    import sys
    PassengerChecker().run(sys.argv[1:])