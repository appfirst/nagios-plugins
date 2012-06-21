#!/usr/bin/python
'''
Created on Jun 11, 2012

@author: yangming
'''
import nagios
from nagios import BatchStatusPlugin as batch
import commands
import statsd

class MemcachedChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MemcachedChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='memcached_stats', type=str, required=False);
        self.parser.add_argument("-H", "--host", required=False, type=str, default="localhost");
        self.parser.add_argument("-p", "--port", required=False, type=str, default="11211");

    def retrieve_current_status(self, request):
        stats = {}
        cmd = "echo 'stats' | nc"
        cmd += " %s %s" % (request.host, request.port)
        output = commands.getoutput(cmd)
        if "STAT" not in output or "END" not in output:
            return stats
        for l in output.split('\r\n'):
            triple = l.split(" ")
            if triple[0] != "STAT":
                continue
            k = triple[1]
            v = triple[2]
            stats[k] = v
            try:
                stats[k] = int(v)
            except ValueError:
                try:
                    stats[k] = float(v)
                except ValueError:
                    pass
        return stats

    @nagios.BatchStatusPlugin.command("OPERATIONS_SET_REQUESTS", batch.cumulative)
    @statsd.counter("sys.app.memcached.cmd_set_requests")
    def get_cmd_set(self, request):
        # since last time
        queries = self.get_delta_value("cmd_set")
        sec = self.get_delta_value("uptime")
        value = queries
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s set requests in %s' % (value, sec));
        r.add_performance_data('set_requests', value, warn=request.warn, crit=request.crit)

        # rate
        if sec == 0:
            sec = 1
        value = queries / sec
        r.add_performance_data('set_requests_rate', value, warn=request.warn, crit=request.crit)
        return r

    @nagios.BatchStatusPlugin.command("OPERATIONS_GET_REQUESTS", batch.cumulative)
    @statsd.counter("sys.app.memcached.cmd_get_requests")
    def get_cmd_get(self, request):
        # since last time
        queries = self.get_delta_value("cmd_get")
        sec = self.get_delta_value("uptime")
        value = queries
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s get requests in %s' % (value, sec));
        r.add_performance_data('get_requests', value, warn=request.warn, crit=request.crit)

        # rate
        if sec == 0:
            sec = 1
        value = queries / sec
        r.add_performance_data('get_requests_rate', value, warn=request.warn, crit=request.crit)
        return r

    @nagios.BatchStatusPlugin.command("BYTES_READ", batch.cumulative)
    @statsd.counter("sys.app.memcached.bytes_read")
    def get_bytes_read(self, request):
        # since last time
        total_bytes = self.get_delta_value("bytes_read")
        sec = self.get_delta_value("uptime")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes read in %s' % (value, sec));
        r.add_performance_data('bytes_read', value, warn=request.warn, crit=request.crit)

        # rate
        if sec == 0:
            sec = 1
        value = total_bytes / sec
        r.add_performance_data('bytes_read_rate', value, warn=request.warn, crit=request.crit)
        return r

    @nagios.BatchStatusPlugin.command("BYTES_WRITTEN", batch.cumulative)
    @statsd.counter("sys.app.memcached.bytes_written")
    def get_bytes_written(self, request):
        # since last time
        total_bytes = self.get_delta_value("bytes_written")
        sec = self.get_delta_value("uptime")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes written in %s' % (value, sec));
        r.add_performance_data('bytes_written', value, warn=request.warn, crit=request.crit)

        # rate
        if sec == 0:
            sec = 1
        value = total_bytes / sec
        r.add_performance_data('bytes_written_rate', value, warn=request.warn, crit=request.crit)
        return r

    @nagios.BatchStatusPlugin.command("BYTES_ALLOCATED", batch.cumulative)
    @statsd.counter("sys.app.memcached.bytes_allocated")
    def get_bytes_allocated(self, request):
        # since last time
        total_bytes = self.get_delta_value("bytes")
        sec = self.get_delta_value("uptime")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes allocated in %s' % (value, sec));
        r.add_performance_data('bytes_allocated', value, warn=request.warn, crit=request.crit)

        # rate
        if sec == 0:
            sec = 1
        value = total_bytes / sec
        r.add_performance_data('bytes_allocated_rate', value, warn=request.warn, crit=request.crit)
        return r

    @nagios.BatchStatusPlugin.command("TOTAL_ITEMS", batch.status)
    @statsd.gauge("sys.app.memcached.total_items")
    def get_total_items(self, request):
        # since last time
        value = self.stats["total_items"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total items' % value);
        r.add_performance_data('items', value, warn=request.warn, crit=request.crit)
        return r

    @nagios.BatchStatusPlugin.command("TOTAL_CONNECTIONS", batch.status)
    @statsd.gauge("sys.app.memcached.total_connections")
    def get_total_connections(self, request):
        # since last time
        value = self.stats["total_connections"]
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total connections' % value);
        r.add_performance_data('connections', value, warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    import sys
    MemcachedChecker().run(sys.argv[1:])