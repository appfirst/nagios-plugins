#!/usr/bin/env python
'''
Created on Jun 11, 2012

@author: Yangming
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd

class MemcachedChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MemcachedChecker, self).__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--filename", default='memcached_stats', type=str, required=False);
        self.parser.add_argument("-H", "--host", required=False, type=str, default="localhost");
        self.parser.add_argument("-p", "--port", required=False, type=str, default="11211");

    def retrieve_current_status(self, attr, request):
        cmd = "echo 'stats' | nc"
        cmd += " %s %s" % (request.host, request.port)
        output = commands.getoutput(cmd)
        if output.strip() == "":
            cmd = "exec 5<>/dev/tcp/%s/%s;echo -e \"stats\nquit\" >&5;cat <&5" % (request.host, request.port)
            output = commands.getoutput(cmd)
        self.validate_output(request, output)
        for l in output.split('\r\n'):
            triple = l.split(" ")
            if triple[0] != "STAT":
                continue
            k = triple[1]
            v = triple[2]
            if attr == k:
                try:
                    return int(v)
                except ValueError:
                    try:
                        return float(v)
                    except ValueError:
                        raise nagios.OutputFormatError(request, output)
        raise nagios.StatusUnknownError(request, output)

    def validate_output(self, request, output):
        if output.strip() == "":
            raise nagios.ServiceInaccessibleError(request)
        elif "STAT" not in output or "END" not in output:
            raise nagios.ServiceInaccessibleError(request, output)
        return True

    @plugin.command("OPERATIONS_SET_REQUESTS")
    @statsd.counter("sys.app.memcached.operations_set_requests")
    def get_cmd_set(self, request):
        # since last time
        queries = self.get_delta_value(request, "cmd_set")
        value = queries
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s set requests' % value);
        r.add_performance_data('set_requests', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("OPERATIONS_GET_REQUESTS")
    @statsd.counter("sys.app.memcached.operations_get_requests")
    def get_cmd_get(self, request):
        # since last time
        queries = self.get_delta_value(request,"cmd_get")
        value = queries
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s get requests' % value);
        r.add_performance_data('get_requests', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("BYTES_READ")
    @statsd.counter("sys.app.memcached.bytes_read")
    def get_bytes_read(self, request):
        # since last time
        total_bytes = self.get_delta_value(request,"bytes_read")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes read' % value);
        r.add_performance_data('bytes_read', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("BYTES_WRITTEN")
    @statsd.counter("sys.app.memcached.bytes_written")
    def get_bytes_written(self, request):
        # since last time
        total_bytes = self.get_delta_value(request,"bytes_written")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes written' % value);
        r.add_performance_data('bytes_written', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("BYTES_ALLOCATED")
    @statsd.gauge("sys.app.memcached.bytes_allocated")
    def get_bytes_allocated(self, request):
        # since last time
        total_bytes = self.get_delta_value(request,"bytes")
        value = total_bytes
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s bytes allocated' % value);
        r.add_performance_data('bytes_allocated', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TOTAL_ITEMS")
    @statsd.gauge("sys.app.memcached.total_items")
    def get_total_items(self, request):
        value = self.retrieve_current_status("total_items", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total items' % value);
        r.add_performance_data('items', value, warn=request.warn, crit=request.crit)
        return r

    @plugin.command("TOTAL_CONNECTIONS")
    @statsd.gauge("sys.app.memcached.total_connections")
    def get_total_connections(self, request):
        value = self.retrieve_current_status("total_connections", request)
        status_code = self.verdict(value, request)
        r = nagios.Result(request.type, status_code, '%s total connections' % value);
        r.add_performance_data('connections', value, warn=request.warn, crit=request.crit)
        return r

if __name__ == "__main__":
    import sys
    MemcachedChecker().run(sys.argv[1:])