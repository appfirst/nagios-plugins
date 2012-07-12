#!/usr/bin/env python
'''
Created on May 31, 2012

@author: Yangming
'''
import re
import commands
import statsd
import nagios
from nagios import CommandBasedPlugin as plugin

class RedisChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(RedisChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='redis-cli_info', type=str, required=False);

    def retrieve_current_status(self, attr, request):
        value = None
        cmd = "redis-cli info"
        output = commands.getoutput(cmd)
        if "command not found" in output:
            raise nagios.ServiceInaccessibleError(request, output)
        for l in output.split('\r\n'):
            k, v = l.split(':')
            if attr == k:
                try:
                    value = int(v)
                except ValueError:
                    try:
                        value = float(v)
                    except ValueError:
                        raise nagios.OutputFormatError(request, output)
                return value
        raise nagios.StatusUnknownError(request, output)

    @plugin.command("CURRENT_OPERATIONS")
    @statsd.counter("sys.app.redis.current_operations")
    def get_current_operations_rate(self, request):
        # current
        value = self.get_delta_value(request, "total_commands_processed")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands' % value);
        r.add_performance_data('current_commands', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("AVERAGE_OPERATIONS_RATE")
    @statsd.gauge("sys.app.redis.average_operations_rate")
    def get_average_operations_rate(self, request):
        # average
        queries = self.retrieve_current_status("total_commands_processed", request)
        sec = self.retrieve_current_status("uptime_in_seconds", request)
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands per second' % value);
        r.add_performance_data('average_rate', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("READ_WRITE_RATIO")
    @statsd.gauge("sys.app.redis.read_write_ratio")
    def get_read_write_ratio(self, request):
        return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

    @plugin.command("MEMORY_USED")
    @statsd.gauge("sys.app.redis.memory_used")
    def get_memory_used(self, request):
        stats = self.retrieve_current_status("used_memory", request)
        value = float(stats) / 1024 / 1024
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%sMB used_memory" % value);
        r.add_performance_data("used_memory", value, "MB", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("CHANGES_SINCE_LAST_SAVE")
    @statsd.gauge("sys.app.redis.changes_since_last_save")
    def get_changes_since_last_save(self, request):
        value = self.retrieve_current_status("changes_since_last_save", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s changes since last save" % value);
        r.add_performance_data("changes", value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TOTAL_KEYS")
    @statsd.gauge("sys.app.redis.total_keys")
    def get_total_keys(self, request):
        cmd = "redis-cli dbsize"
        output = commands.getoutput(cmd)
        dbsize_pattern = re.compile(".*?(\d+)")
        matchResult = dbsize_pattern.match(output)
        if not matchResult:
            raise nagios.OutputFormatError(request, output)
        value = int(matchResult.groups(1)[0])
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total keys' % value);
        r.add_performance_data('total_keys', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("COMMAND_FREQUENCY")
    @statsd.gauge("sys.app.redis.command_frequency")
    def get_command_frequency(self, request):
        return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

if __name__ == "__main__":
    import sys
    RedisChecker().run(sys.argv[1:])