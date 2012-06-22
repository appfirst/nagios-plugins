'''
Created on Jun 22, 2012

@author: Yangming
'''
import re
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd
from datetime import timedelta

class MongoDBChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MongoDBChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='mongostat', type=str, required=False);

    def retrieve_current_status(self, request):
        cmd = "mongostat -n 1 --noheaders"
        stats = {}
        output = commands.getoutput(cmd)
        if "command not found" in output or "ERROR" in output:
            return stats
        fields = output.split('\n')[1].strip().split()
        headers = ["insert",     "query",   "update",  "delete",
                   "getmore",    "command", "flushes", "mapped",
                   "vsize",      "res",     "faults",  "locked %",
                   "idx miss %", "qr|qw",   "ar|aw",   "netIn",
                   "netOut",     "conn",    "time"]
        for k, v in zip(headers, fields):
            if k == "time":
                uptime = [int(t) for t in v.split(":")]
                sec = timedelta(hours=uptime[0],
                              minutes=uptime[1],
                              seconds=uptime[2]).total_seconds()
                stats[k] = sec
            elif k == "res":
                pattern = re.compile('(\d+)m')
                matchResult = pattern.match(v)
                value = int(matchResult.groups(1)[0])
                stats[k] = value
            else:
                try:
                    stats[k] = int(v)
                except ValueError:
                    try:
                        stats[k] = float(v)
                    except ValueError:
                        stats[k] = v
        return stats

    @plugin.command("CONNECTIONS", nagios.BatchStatusPlugin.cumulative)
    @statsd.counter("sys.app.mongodb.connections")
    def get_connections(self, request):
        value = self.get_delta_value("conn")
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s new connections' % value);
        r.add_performance_data('conns', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MEMORY_USED", nagios.BatchStatusPlugin.status)
    @statsd.counter("sys.app.mongodb.memory_used")
    def get_memory_used(self, request):
        value = self.stats["res"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%sMB resident size' % value);
        r.add_performance_data('res', value, UOM='MB', warn=request.warn, crit=request.crit)
        return r

    @plugin.command("INSERT_RATE", nagios.BatchStatusPlugin.cumulative)
    @statsd.counter("sys.app.mongodb.insert_rate")
    def get_insert_rate(self, request):
        queries = self.get_delta_value("insert")
        sec = self.get_delta_value("time")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s inserts per sec' % value);
        r.add_performance_data('rate', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("UPDATE_RATE", nagios.BatchStatusPlugin.cumulative)
    @statsd.counter("sys.app.mongodb.update_rate")
    def get_update_rate(self, request):
        queries = self.get_delta_value("update")
        sec = self.get_delta_value("time")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s updates per sec' % value);
        r.add_performance_data('rate', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("COMMAND_RATE", nagios.BatchStatusPlugin.cumulative)
    @statsd.counter("sys.app.mongodb.command_rate")
    def get_command_rate(self, request):
        queries = self.get_delta_value("command")
        sec = self.get_delta_value("time")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s commands per sec' % value);
        r.add_performance_data('rate', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("QUERY_RATE", nagios.BatchStatusPlugin.cumulative)
    @statsd.counter("sys.app.mongodb.query_rate")
    def get_query_rate(self, request):
        queries = self.get_delta_value("query")
        sec = self.get_delta_value("time")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s queries per sec' % value);
        r.add_performance_data('rate', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("DELETE_RATE", nagios.BatchStatusPlugin.cumulative)
    @statsd.counter("sys.app.mongodb.delete_rate")
    def get_delete_rate(self, request):
        queries = self.get_delta_value("delete")
        sec = self.get_delta_value("time")
        value = queries / sec
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s deletes per sec' % value);
        r.add_performance_data('rate', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("LOCKED_PERCENTAGE", nagios.BatchStatusPlugin.status)
    @statsd.counter("sys.app.mongodb.locked_ratio")
    def get_locked_ratio(self, request):
        value = self.stats["locked %"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% locked');
        r.add_performance_data('ratio', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

    @plugin.command("MISS_PERCENTAGE", nagios.BatchStatusPlugin.status)
    @statsd.counter("sys.app.mongodb.miss_ratio")
    def get_miss_ratio(self, request):
        value = self.stats["idx miss %"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, str(value) + '% missed');
        r.add_performance_data('ratio', value, UOM="%", warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    import sys
    MongoDBChecker().run(sys.argv[1:])