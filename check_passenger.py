#!/usr/bin/env python
'''
Created on Jun 7, 2012

@author: Yangming
@copyright: appfirst inc.
'''
import commands
import statsd
import nagios
from nagios import CommandBasedPlugin as plugin

class PassengerChecker(nagios.CommandBasedPlugin):
    def __init__(self, *args, **kwargs):
        super(PassengerChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str,
                                 default="passenger-status");
        self.parser.add_argument("-p", "--pid", required=False, type=str);

    def retrieve_current_status(self, attr, request):
        # TODO: make sudo and path optional
        cmd = "sudo /usr/bin/passenger-status"
        output = commands.getoutput(cmd)
        self.validate_output(request, output)
        for l in output.split('\n'):
            pair = l.split('=')
            if len(pair) == 2:
                k = pair[0].strip()
                v = pair[1].strip()
                if attr == k:
                    try:
                        return int(v)
                    except ValueError:
                        try:
                            return float(v)
                        except ValueError:
                            raise nagios.OutputFormatError(request, output)
        raise nagios.StatusUnknownError(request)

    def validate_output(self, request, output):
        if "command not found" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        if "ERROR: You are not authorized" in output:
            raise nagios.AuthenticationFailedError(request, output)
        elif "ERROR" in output:
            raise nagios.StatusUnknownError(request, output)
        return True

    @plugin.command("RUNNING_PROCESSES")
    @statsd.gauge("sys.app.passenger.max_processes")
    def get_procs(self, request):
        value = self.retrieve_current_status("count", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s running processes" % value);
        r.add_performance_data("running_procs", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MAX_PROCESSES")
    @statsd.gauge("sys.app.passenger.running_processes")
    def get_max_procs(self, request):
        value = self.retrieve_current_status("max", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s max processes" % value);
        r.add_performance_data("max", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("ACTIVE_PROCESSES")
    @statsd.gauge("sys.app.passenger.active_processes")
    def get_active_procs(self, request):
        value = self.retrieve_current_status("active", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s active processes" % value);
        r.add_performance_data("active", value, warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    import sys
    PassengerChecker().run(sys.argv[1:])