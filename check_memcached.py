#!/usr/bin/env python
'''
Created on Jun 11, 2012
Updated on September 19, 2014 by Tony Ling

@author: Yangming
'''
import nagios
from nagios import CommandBasedPlugin as plugin
import commands
import statsd
import argparse

class MemcachedChecker(nagios.BatchStatusPlugin):
    def __init__(self, *args, **kwargs):
        super(MemcachedChecker, self).__init__(*args, **kwargs)
        # Hack to determine uniqueness of script defs
        check = argparse.ArgumentParser()
        check.add_argument("-H", "--host",     required=False, type=str)
        check.add_argument("-p", "--port",     required=False, type=int)
        chk, unknown = check.parse_known_args()

        self.parser.add_argument("-f", "--filename", required=False, type=str, default='pd@memcached_stats')
        self.parser.add_argument("-H", "--host",     required=False, type=str, default="localhost")
        self.parser.add_argument("-p", "--port",     required=False, type=int, default=11211)
        self.parser.add_argument("-z", "--appname",  required=False, type=str, default='memcached')
        self.parser.add_argument("--unique",   required=False, type=str, default=str(chk.host)+str(chk.port))

    def _get_batch_status(self, request):
        cmd = "echo 'stats' | nc"
        cmd += " %s %s" % (request.host, request.port)
#        output = commands.getoutput(cmd)
#        if output.strip() == "":
        import subprocess
        cmd = "exec 5<>/dev/tcp/%s/%s;echo -e \"stats\nquit\" >&5;cat <&5" % (request.host, request.port)
        proc = subprocess.Popen(['bash', '-c', cmd],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        output, _ = proc.communicate()
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
    @statsd.counter
    def get_cmd_set(self, request):
        value = self.get_delta_value("cmd_set", request)
        return self.get_result(request, value, '%s set requests' % value, 'set_requests')

    @plugin.command("OPERATIONS_GET_REQUESTS")
    @statsd.counter
    def get_cmd_get(self, request):
        value = self.get_delta_value("cmd_get", request)
        return self.get_result(request, value, '%s get resquests' % value, 'get_requests')

    @plugin.command("BYTES_READ")
    @statsd.counter
    def get_bytes_read(self, request):
        value = self.get_delta_value("bytes_read", request)
        return self.get_result(request, value, '%s bytes read' % value, 'bytes_read')

    @plugin.command("BYTES_WRITTEN")
    @statsd.counter
    def get_bytes_written(self, request):
        value = self.get_delta_value("bytes_written", request)
        return self.get_result(request, value, '%s bytes written' % value, 'bytes_written')

    @plugin.command("BYTES_ALLOCATED")
    @statsd.gauge
    def get_bytes_allocated(self, request):
        value = self.get_status_value("bytes", request)
        return self.get_result(request, value, '%s bytes allocated' % value, 'bytes')

    @plugin.command("TOTAL_ITEMS")
    @statsd.gauge
    def get_total_items(self, request):
        value = self.get_status_value("total_items", request)
        return self.get_result(request, value, '%s total items' % value, 'total_items')

    @plugin.command("CURRENT_CONNECTIONS")
    @statsd.gauge
    def get_current_connections(self, request):
        value = self.get_status_value("curr_connections", request)
        return self.get_result(request, value, '%s current connections' % value, "connections")

    @plugin.command("CACHE_EVICTIONS")
    @statsd.gauge
    def get_cache_evictions(self, request):
        value = self.get_status_value("evictions", request)
        return self.get_result(request, value, '%s cache evictions' % value, "evictions")

    @plugin.command("CACHE_RECLAIMED")
    @statsd.gauge
    def get_cache_reclaimed(self, request):
        value = self.get_status_value("reclaimed", request)
        return self.get_result(request, value, '%s cache reclaimed' % value, "reclaimed")

    @plugin.command("OPERATIONS_FLUSH_REQUESTS")
    @statsd.counter
    def get_cmd_flush(self, request):
        value = self.get_delta_value("cmd_flush", request)
        return self.get_result(request, value, '%s flush requests' % value, 'cmd_flush')

    @plugin.command("OPERATIONS_TOUCH_REQUESTS")
    @statsd.counter
    def get_cmd_touch(self, request):
        value = self.get_delta_value("cmd_touch", request)
        return self.get_result(request, value, '%s touch requests' % value, 'cmd_touch')

    @plugin.command("CURRENT_ITEMS")
    @statsd.counter
    def get_current_items(self, request):
        value = self.get_status_value("curr_items", request)
        return self.get_result(request, value, '%s current items' % value, 'curr_items')

    @plugin.command("HIT_RATIO")
    @statsd.counter
    def get_hit_ratio(self, request):
        hits = self.get_status_value("get_hits", request)
        misses = self.get_status_value("get_misses", request)
	total = hits+misses
	if (total > 0):
		value = (hits*1.0)/(total)
	else:
		value = 0
        return self.get_result(request, value, '%s hit ratio' % value, 'hit_ratio')

    @plugin.command("THREADS")
    @statsd.counter
    def get_threads(self, request):
        value = self.get_delta_value("threads", request)
        return self.get_result(request, value, '%s threads' % value, 'threads')

if __name__ == "__main__":
    import sys
    MemcachedChecker().run(sys.argv[1:])
