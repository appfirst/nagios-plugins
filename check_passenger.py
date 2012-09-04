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

class PassengerChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(PassengerChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", required=False, type=str, default="pd@passenger-status")
        self.parser.add_argument("-p", "--pid",      required=False, type=str)
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='passenger')

    def _get_batch_status(self, request):
        # TODO: make path optional
        cmd = nagios.rootify("/usr/bin/passenger-status")
        return commands.getoutput(cmd)

    def _parse_output(self, request, output):
        for l in output.split('\n'):
            pair = l.split('=')
            if len(pair) == 2:
                k = pair[0].strip()
                v = pair[1].strip()
                value = nagios.to_num(v)
                if value is None:
                    raise nagios.OutputFormatError(request, output)
                yield k, value

    def _validate_output(self, request, output):
        if "command not found" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "ERROR: Phusion Passenger doesn't seem to be running." in output:
            raise nagios.ServiceInaccessibleError(request, output)
        elif "ERROR: You are not authorized" in output:
            raise nagios.AuthenticationFailedError(request, output)
        elif "ERROR" in output:
            raise nagios.StatusUnknownError(request, output)
        return True

    @plugin.command("RUNNING_PROCESSES")
    @statsd.gauge
    def get_procs(self, request):
        value = self.get_status_value("count", request)
        return self.get_result(request, value, '%s running processes' % value, 'procs')

    @plugin.command("MAX_PROCESSES")
    @statsd.gauge
    def get_max_procs(self, request):
        value = self.get_status_value("max", request)
        return self.get_result(request, value, '%s max processes' % value, 'max')

    @plugin.command("ACTIVE_PROCESSES")
    @statsd.gauge
    def get_active_procs(self, request):
        value = self.get_status_value("active", request)
        return self.get_result(request, value, '%s active processes' % value, 'active')

if __name__ == "__main__":
    import sys
    PassengerChecker().run(sys.argv[1:])