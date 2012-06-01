'''
Created on May 31, 2012

@author: appfirst
'''
import re
import nagios
import commands

class RedisChecker(nagios.BatchStatusPlugin):
    def __init__(self):
        super(RedisChecker, self).__init__()
        self.parser.add_argument("-f", "--filename", default='redis-cli-info', type=str, required=False);
        choices = ["CUR_OPERATIONS_RATE",
                   "AVG_OPERATIONS_RATE",
                   "MEMORY_USED",
                   "CHANGES_SINCE_LAST_SAVE",
                   "READ_WRITE_RATIO",
                   "TOTAL_KEYS",
                   "COMMAND_FREQUENCY"]
        self.parser.add_argument("-t", "--type", choices=choices, required=True);
        self.parser.add_argument("-u", "--user", type=str, required=False);
        self.parser.add_argument("-p", "--password", type=str, required=False);

    def check(self, request):
        if request.type == 'TOTAL_KEYS':
            return self.get_total_keys(request)
        self.stats = self.parse_status_output(request)
        if len(self.stats) == 0:
            return nagios.Result(request.type,nagios.Status.UNKNOWN,
                                 "failed to check redis. check arguments and try again.")
        if request.type == 'CUR_OPERATIONS_RATE':
            return self.get_current_operations_rate(request)
        if request.type == 'AVG_OPERATIONS_RATE':
            return self.get_average_operations_rate(request)
        if request.type == 'MEMORY_USED':
            return self.get_memory_used(request)
        if request.type == 'CHANGES_SINCE_LAST_SAVE':
            return self.get_changes_since_last_save(request)
        if request.type == 'READ_WRITE_RATIO':
            return nagios.Result(request.type,nagios.Status.UNKNOWN,"mysterious status")
        if request.type == 'COMMAND_FREQUENCY':
            return self.get_command_frequency(request)

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

    def get_current_operations_rate(self, request):
        queries = self.get_delta_value("total_commands_processed")
        sec = self.get_delta_value("uptime_in_seconds")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands per second' % value);
        r.add_performance_data('frequency', value, warn=request.warn, crit=request.crit)
        return r

    def get_average_operations_rate(self, request):
        queries = self.stats["total_commands_processed"]
        sec = self.stats["uptime_in_seconds"]
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands per second' % value);
        r.add_performance_data('frequency', value, warn=request.warn, crit=request.crit)
        return r

    def get_memory_used(self, request):
        value = float(self.stats["used_memory"]) / 1024 / 1024
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%sMB used_memory" % value);
        r.add_performance_data("used_memory", value, "MB", warn=request.warn, crit=request.crit)
        return r

    def get_changes_since_last_save(self, request):
        value = self.stats["changes_since_last_save"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, "%s changes since last save" % value);
        r.add_performance_data("changes", value, warn=request.warn, crit=request.crit)
        return r

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

    def get_command_frequency(self, request):
        queries = self.get_delta_value("total_commands_processed")
        sec = self.get_delta_value("uptime_in_seconds")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands per second' % value);
        r.add_performance_data('frequency', value, warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    RedisChecker().run()