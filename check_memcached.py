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
        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@memcached_stats');
        self.parser.add_argument("-H", "--host",     required=False, type=str, default="localhost");
        self.parser.add_argument("-p", "--port",     required=False, type=int, default=11211);

    def _get_batch_status(self, request):
        cmd = "echo 'stats' | nc"
        cmd += " %s %s" % (request.host, request.port)
        output = commands.getoutput(cmd)
        if output.strip() == "":
            cmd = "exec 5<>/dev/tcp/%s/%s;echo -e \"stats\nquit\" >&5;cat <&5" % (request.host, request.port)
            output = commands.getoutput(cmd)
        return output

    def _parse_output(self, request, output):
        for l in output.split('\r\n'):
            triple = l.split(" ")
            if triple[0] != "STAT":
                continue
            k = triple[1]
            v = triple[2]
            value = nagios.to_num(v)
            if value is not None:
                yield k, value

    def _validate_output(self, request, output):
        if output.strip() == "":
            raise nagios.ServiceInaccessibleError(request)
        elif "STAT" not in output or "END" not in output:
            raise nagios.ServiceInaccessibleError(request, output)
        return True

    @plugin.command("OPERATIONS_SET_REQUESTS")
    @statsd.counter("sys.app.memcached.operations_set_requests")
    def get_cmd_set(self, request):
        value = self.get_delta_value("cmd_set", request)
        return self.get_result(request, value, '%s set requests' % value, 'set_requests')

    @plugin.command("OPERATIONS_GET_REQUESTS")
    @statsd.counter("sys.app.memcached.operations_get_requests")
    def get_cmd_get(self, request):
        value = self.get_delta_value("cmd_get", request)
        return self.get_result(request, value, '%s get resquests' % value, 'get_requests')

    @plugin.command("BYTES_READ")
    @statsd.counter("sys.app.memcached.bytes_read")
    def get_bytes_read(self, request):
        value = self.get_delta_value("bytes_read", request)
        return self.get_result(request, value, '%s bytes read' % value, 'bytes_read')

    @plugin.command("BYTES_WRITTEN")
    @statsd.counter("sys.app.memcached.bytes_written")
    def get_bytes_written(self, request):
        value = self.get_delta_value("bytes_written", request)
        return self.get_result(request, value, '%s bytes written' % value, 'bytes_written')

    @plugin.command("BYTES_ALLOCATED")
    @statsd.gauge("sys.app.memcached.bytes_allocated")
    def get_bytes_allocated(self, request):
        value = self.get_delta_value("bytes", request)
        return self.get_result(request, value, '%s bytes allocated' % value, 'bytes_allocated')

    @plugin.command("TOTAL_ITEMS")
    @statsd.gauge("sys.app.memcached.total_items")
    def get_total_items(self, request):
        value = self.get_status_value("total_items", request)
        return self.get_result(request, value, '%s total items' % value, 'items')

    @plugin.command("TOTAL_CONNECTIONS")
    @statsd.gauge("sys.app.memcached.total_connections")
    def get_total_connections(self, request):
        value = self.get_status_value("total_connections", request)
        return self.get_result(request, value, '%s total connections' % value, "connections")

if __name__ == "__main__":
    import sys
    MemcachedChecker().run(sys.argv[1:])