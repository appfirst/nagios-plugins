#!/usr/bin/python
'''
Created on May 31, 2012

@author: yangming
'''
import re
import nagios
from nagios import BatchStatusPlugin
import commands
import statsd

class RedisChecker(BatchStatusPlugin):
    def __init__(self):
        super(RedisChecker, self).__init__()
        self.parser.add_argument("-f", "--filename", default='redis-cli_info', type=str, required=False);

    def parse_status_output(self, request):
        stats = {}
        cmd = "redis-cli info"
        output = commands.getoutput(cmd)
        if "command not found" in output:
            return stats
        for l in output.split('\r\n'):
            k, v = l.split(':')
            stats[k] = v
            try:
                stats[k] = int(v)
            except ValueError:
                try:
                    stats[k] = float(v)
                except ValueError:
                    pass
        return stats

    @BatchStatusPlugin.command("OPERATIONS_RATE", "cumulative")
    @statsd.counter("sys.app.redis.operations_rate")
    def get_operations_rate(self, request):
        # current
        queries = self.get_delta_value("total_commands_processed")
        sec = self.get_delta_value("uptime_in_seconds")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands per second' % value);
        r.add_performance_data('current_rate', value, warn=request.warn, crit=request.crit)

        # average
        queries = self.stats["total_commands_processed"]
        sec = self.stats["uptime_in_seconds"]
        value = queries / sec
        r.add_performance_data('average_rate', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("READ_WRITE_RATIO")
    @statsd.counter("sys.app.redis.read_write_ratio")
    def get_read_write_ratio(self, request):
        return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

    @BatchStatusPlugin.command("MEMORY_USED", "status")
    @statsd.gauge("sys.app.redis.memory_used")
    def get_memory_used(self, request):
        value = float(self.stats["used_memory"]) / 1024 / 1024
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%sMB used_memory" % value);
        r.add_performance_data("used_memory", value, "MB", warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("CHANGES_SINCE_LAST_SAVE", "status")
    @statsd.gauge("sys.app.redis.changes_since_last_save")
    def get_changes_since_last_save(self, request):
        value = self.stats["changes_since_last_save"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s changes since last save" % value);
        r.add_performance_data("changes", value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("TOTAL_KEYS")
    @statsd.gauge("sys.app.redis.total_keys")
    def get_total_keys(self, request):
        cmd = "redis-cli dbsize"
        output = commands.getoutput(cmd)
        dbsize_pattern = re.compile(".*?(\d+)")
        matchResult = dbsize_pattern.match(output)
        if not matchResult:
            return nagios.Result(request.type,nagios.Status.UNKNOWN,
                                 "failed to check redis. check arguments and try again.")
        value = int(matchResult.groups(1)[0])
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total keys' % value);
        r.add_performance_data('total_keys', value, warn=request.warn, crit=request.crit)
        return r

    @BatchStatusPlugin.command("COMMAND_FREQUENCY")
    @statsd.counter("sys.app.redis.command_frequency")
    def get_command_frequency(self, request):
        return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

if __name__ == "__main__":
    RedisChecker().run()