#!/usr/bin/python
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
        self.choicemap = {"OPERATIONS_RATE"        :self.get_operations_rate,
                          "MEMORY_USED"            :self.get_memory_used,
                          "CHANGES_SINCE_LAST_SAVE":self.get_changes_since_last_save,
                          "READ_WRITE_RATIO"       :None,
                          "TOTAL_KEYS"             :self.get_total_keys,
                          "COMMAND_FREQUENCY"      :None}
        self.parser.add_argument("-f", "--filename", default='redis-cli_info', type=str, required=False);
        self.parser.add_argument("-t", "--type", required=True, choices=self.choicemap.keys());

    def check(self, request):
        if request.type == 'TOTAL_KEYS':
            return self.get_total_keys(request)
        self.stats = self.parse_status_output(request)
        if len(self.stats) == 0:
            return nagios.Result(request.type,nagios.Status.CRITICAL,
                                 "cannot connect to redis.")
        if request.type in self.choicemap and self.choicemap[request.type]:
            return self.choicemap[request.type](request)
        else:
            return nagios.Result(request.type, nagios.Status.UNKNOWN,
                                 "mysterious status")

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

if __name__ == "__main__":
    RedisChecker().run()